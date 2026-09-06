/*
 * Copyright (C) 2026 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#define LOG_TAG "sensors.qsh.manet"

#include <V2_1/SubHal.h>
#include <android/hardware/sensors/1.0/types.h>
#include <android/hardware/sensors/2.1/types.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <log/log.h>
#include <poll.h>
#include <sys/eventfd.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <utils/SystemClock.h>

#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>

namespace android::hardware::sensors::V2_1::implementation {

using V1_0::OperationMode;
using V1_0::RateLevel;
using V1_0::Result;
using V1_0::SensorFlagBits;
using V1_0::SharedMemInfo;

namespace {

constexpr char kStockSubHalPath[] = "/vendor/lib64/sensors.qsh.so";
constexpr char kFodSensorType[] = "xiaomi.sensor.fod_detector";
constexpr char kFodStatusPath[] = "/sys/class/touch/touch_dev/fod_press_status";
constexpr char kTouchDevicePath[] = "/dev/xiaomi-touch";
constexpr int kTouchId = 0;
constexpr int kTouchFodEnableMode = 10;
constexpr float kFodDownEventValue = 3.0f;

struct TouchFeatureMode {
    uint8_t touchId;
    uint8_t command;
    uint16_t mode;
    uint16_t valueCount;
    uint16_t reserved;
    int32_t values[128];
};

static_assert(sizeof(TouchFeatureMode) == 520);

#define TOUCH_IOC_SETMODE _IOWR('T', 0, TouchFeatureMode)
#define TOUCH_IOC_SELECT_TOUCH _IOW('T', 3, int)

using GetSubHal = ISensorsSubHal* (*)(uint32_t* version);

class QshSensorsSubHal final : public ISensorsSubHal {
  public:
    QshSensorsSubHal() {
        mLibrary = dlopen(kStockSubHalPath, RTLD_NOW | RTLD_LOCAL);
        if (mLibrary == nullptr) {
            ALOGE("Failed to load %s: %s", kStockSubHalPath, dlerror());
            std::abort();
        }

        auto getSubHal = reinterpret_cast<GetSubHal>(
                dlsym(mLibrary, "sensorsHalGetSubHal_2_1"));
        if (getSubHal == nullptr) {
            ALOGE("Stock QSH SubHAL entry point is missing: %s", dlerror());
            std::abort();
        }

        uint32_t version = 0;
        mInner = getSubHal(&version);
        if (mInner == nullptr || version != SUB_HAL_2_1_VERSION) {
            ALOGE("Invalid stock QSH SubHAL version: 0x%x", version);
            std::abort();
        }

        mControlFd = eventfd(0, EFD_CLOEXEC | EFD_NONBLOCK);
        if (mControlFd < 0) {
            ALOGE("Failed to create FOD control eventfd: %s", strerror(errno));
            std::abort();
        }
        mFodThread = std::thread(&QshSensorsSubHal::fodThreadLoop, this);
    }

    ~QshSensorsSubHal() override {
        mStop = true;
        wakeFodThread();
        if (mFodThread.joinable()) {
            mFodThread.join();
        }
        close(mControlFd);
        if (mLibrary != nullptr) {
            dlclose(mLibrary);
        }
    }

    Return<void> getSensorsList_2_1(
            V2_1::ISensors::getSensorsList_2_1_cb callback) override {
        return mInner->getSensorsList_2_1([this, callback](const hidl_vec<SensorInfo>& sensors) {
            hidl_vec<SensorInfo> patched = sensors;

            for (SensorInfo& sensor : patched) {
                if (sensor.typeAsString == kFodSensorType) {
                    const uint32_t flags = static_cast<uint32_t>(sensor.flags);
                    sensor.flags = (flags & ~static_cast<uint32_t>(
                                             SensorFlagBits::MASK_REPORTING_MODE)) |
                                   static_cast<uint32_t>(SensorFlagBits::ONE_SHOT_MODE);
                    mFodHandle = sensor.sensorHandle;
                    mFodSensorType = sensor.type;
                    ALOGI("Patched %s sensor handle %d flags from 0x%x to 0x%x",
                          sensor.typeAsString.c_str(), sensor.sensorHandle, flags,
                          static_cast<uint32_t>(sensor.flags));
                }
            }
            callback(patched);
        });
    }

    Return<Result> injectSensorData_2_1(const Event& event) override {
        return mInner->injectSensorData_2_1(event);
    }

    Return<Result> initialize(const sp<IHalProxyCallback>& callback) override {
        {
            std::lock_guard<std::mutex> lock(mCallbackMutex);
            mCallback = callback;
        }
        return mInner->initialize(callback);
    }

    Return<Result> setOperationMode(OperationMode mode) override {
        return mInner->setOperationMode(mode);
    }

    Return<Result> activate(int32_t sensorHandle, bool enabled) override {
        if (sensorHandle != mFodHandle.load()) {
            return mInner->activate(sensorHandle, enabled);
        }

        // The stock QSH FOD sensor can report a stale event when the pickup
        // gesture wakes the panel. Use the touch driver's press status as the
        // sole event source so pickup and screen-off fingerprint stay independent.
        if (!setTouchFodEnabled(enabled)) {
            ALOGE("Failed to set touch FOD mode to %d", enabled);
            if (enabled) return Result::INVALID_OPERATION;
        }

        mFodActive = enabled;
        wakeFodThread();
        return Result::OK;
    }

    Return<Result> batch(int32_t sensorHandle, int64_t samplingPeriodNs,
                         int64_t maxReportLatencyNs) override {
        return mInner->batch(sensorHandle, samplingPeriodNs, maxReportLatencyNs);
    }

    Return<Result> flush(int32_t sensorHandle) override {
        return mInner->flush(sensorHandle);
    }

    Return<void> registerDirectChannel(
            const SharedMemInfo& mem,
            V2_0::ISensors::registerDirectChannel_cb callback) override {
        return mInner->registerDirectChannel(mem, callback);
    }

    Return<Result> unregisterDirectChannel(int32_t channelHandle) override {
        return mInner->unregisterDirectChannel(channelHandle);
    }

    Return<void> configDirectReport(
            int32_t sensorHandle, int32_t channelHandle, RateLevel rate,
            V2_0::ISensors::configDirectReport_cb callback) override {
        return mInner->configDirectReport(sensorHandle, channelHandle, rate, callback);
    }

    Return<void> debug(const hidl_handle& fd, const hidl_vec<hidl_string>& args) override {
        return mInner->debug(fd, args);
    }

    const std::string getName() override {
        return "QSH manet FOD wrapper (" + mInner->getName() + ")";
    }

  private:
    bool setTouchFodEnabled(bool enabled) {
        int fd = open(kTouchDevicePath, O_RDWR | O_CLOEXEC);
        if (fd < 0) {
            ALOGE("Failed to open %s: %s", kTouchDevicePath, strerror(errno));
            return false;
        }

        if (ioctl(fd, TOUCH_IOC_SELECT_TOUCH, kTouchId) < 0) {
            ALOGE("Failed to select touch id %d: %s", kTouchId, strerror(errno));
            close(fd);
            return false;
        }

        TouchFeatureMode request{};
        request.touchId = kTouchId;
        request.mode = kTouchFodEnableMode;
        request.valueCount = 1;
        request.values[0] = enabled ? 1 : 0;

        const int rc = ioctl(fd, TOUCH_IOC_SETMODE, &request);
        if (rc < 0) {
            ALOGE("Touch FOD ioctl failed: %s", strerror(errno));
        } else {
            ALOGI("Touch FOD mode set to %d", enabled);
        }
        close(fd);
        return rc >= 0;
    }

    void wakeFodThread() {
        uint64_t value = 1;
        if (write(mControlFd, &value, sizeof(value)) < 0 && errno != EAGAIN) {
            ALOGE("Failed to wake FOD thread: %s", strerror(errno));
        }
    }

    static bool readFodStatus(int fd, bool* pressed) {
        char value = '0';
        if (lseek(fd, 0, SEEK_SET) < 0 || read(fd, &value, sizeof(value)) != sizeof(value)) {
            return false;
        }
        *pressed = value == '1';
        return true;
    }

    void fodThreadLoop() {
        int statusFd = open(kFodStatusPath, O_RDONLY | O_CLOEXEC);
        if (statusFd < 0) {
            ALOGE("Failed to open %s: %s", kFodStatusPath, strerror(errno));
            return;
        }

        bool wasPressed = false;
        if (!readFodStatus(statusFd, &wasPressed)) {
            ALOGE("Failed to read initial FOD status: %s", strerror(errno));
        }

        pollfd fds[] = {
                {.fd = statusFd, .events = POLLPRI | POLLERR, .revents = 0},
                {.fd = mControlFd, .events = POLLIN, .revents = 0},
        };
        while (!mStop.load()) {
            if (poll(fds, 2, -1) < 0) {
                if (errno == EINTR) continue;
                ALOGE("FOD status poll failed: %s", strerror(errno));
                break;
            }

            if (fds[1].revents != 0) {
                uint64_t value;
                while (read(mControlFd, &value, sizeof(value)) == sizeof(value)) {}
                bool pressed;
                if (readFodStatus(statusFd, &pressed)) {
                    wasPressed = pressed;
                }
            }

            if (fds[0].revents == 0) continue;
            bool pressed;
            if (!readFodStatus(statusFd, &pressed)) {
                ALOGE("Failed to read FOD status: %s", strerror(errno));
                continue;
            }

            if (mFodActive.load() && pressed && !wasPressed) {
                postFodEvent();
            }
            wasPressed = pressed;
        }
        close(statusFd);
    }

    void postFodEvent() {
        sp<IHalProxyCallback> callback;
        {
            std::lock_guard<std::mutex> lock(mCallbackMutex);
            callback = mCallback;
        }
        if (callback == nullptr) {
            ALOGE("Cannot post FOD event before initialization");
            return;
        }

        Event event{};
        event.timestamp = ::android::elapsedRealtimeNano();
        event.sensorHandle = mFodHandle.load();
        event.sensorType = mFodSensorType;
        event.u.data[0] = kFodDownEventValue;

        mFodActive = false;
        callback->postEvents({event}, callback->createScopedWakelock(true));
        ALOGI("Posted screen-off FOD event");
    }

    void* mLibrary = nullptr;
    ISensorsSubHal* mInner = nullptr;
    int mControlFd = -1;
    std::atomic<bool> mFodActive = false;
    std::atomic<bool> mStop = false;
    std::atomic<int32_t> mFodHandle = -1;
    SensorType mFodSensorType = SensorType::DEVICE_PRIVATE_BASE;
    std::mutex mCallbackMutex;
    sp<IHalProxyCallback> mCallback;
    std::thread mFodThread;
};

QshSensorsSubHal gSubHal;

}  // namespace

}  // namespace android::hardware::sensors::V2_1::implementation

extern "C" __attribute__((visibility("default")))
android::hardware::sensors::V2_1::implementation::ISensorsSubHal*
sensorsHalGetSubHal_2_1(uint32_t* version) {
    *version = SUB_HAL_2_1_VERSION;
    return &android::hardware::sensors::V2_1::implementation::gSubHal;
}
