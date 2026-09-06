/*
 * Copyright (C) 2026 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#define LOG_TAG "UdfpsHandler.xiaomi_manet"

#include <aidl/android/hardware/biometrics/fingerprint/BnFingerprint.h>
#include <android-base/logging.h>

#include <chrono>
#include <fstream>
#include <thread>

#include "UdfpsHandler.h"

namespace {

constexpr int kCommandNit = 10;
constexpr int kParamNitFod = 1;
constexpr int kParamNitNone = 0;

constexpr int kCommandFodPressStatus = 1;
constexpr int kParamFodPressed = 1;
constexpr int kParamFodReleased = 0;

constexpr char kFodStatusPath[] = "/sys/class/touch/touch_dev/fod_press_status";
constexpr char kDispParamPath[] =
        "/sys/devices/virtual/mi_display/disp_feature/disp-DSI-0/disp_param";
constexpr char kLocalHbmOn[] = "9 1";
constexpr char kLocalHbmOff[] = "9 0";

constexpr int kFingerprintAcquiredVendor = 7;
constexpr auto kLocalHbmPollInterval = std::chrono::milliseconds(10);
constexpr auto kLocalHbmTimeout = std::chrono::milliseconds(400);
constexpr auto kLocalHbmSettleTime = std::chrono::milliseconds(20);

template <typename T>
void set(const std::string& path, const T& value) {
    std::ofstream file(path);
    file << value;
}

bool isLocalHbmEnabled() {
    std::ifstream file(kDispParamPath);
    std::string line;
    while (std::getline(file, line)) {
        if (line.find("local_hbm[09]") != std::string::npos) {
            return line.find(": 1") != std::string::npos;
        }
    }
    return false;
}

}  // namespace

using ::aidl::android::hardware::biometrics::fingerprint::AcquiredInfo;

class XiaomiManetUdfpsHandler : public UdfpsHandler {
  public:
    void init(fingerprint_device_t* device) override {
        mDevice = device;
    }

    void onFingerDown(uint32_t /*x*/, uint32_t /*y*/, float /*minor*/, float /*major*/) override {
        LOG(INFO) << __func__;

        // SystemUI renders the icon immediately. The panel may still be resuming
        // from OFF, in which case its first local-HBM command is discarded.
        mDevice->extCmd(mDevice, kCommandNit, kParamNitFod);
        set(kDispParamPath, kLocalHbmOn);

        const auto deadline = std::chrono::steady_clock::now() + kLocalHbmTimeout;
        while (!isLocalHbmEnabled() && std::chrono::steady_clock::now() < deadline) {
            std::this_thread::sleep_for(kLocalHbmPollInterval);
            set(kDispParamPath, kLocalHbmOn);
        }
        if (!isLocalHbmEnabled()) {
            LOG(WARNING) << "Local HBM did not become ready before capture";
        }
        std::this_thread::sleep_for(kLocalHbmSettleTime);
        mDevice->extCmd(mDevice, kCommandFodPressStatus, kParamFodPressed);
    }

    void onFingerUp() override {
        LOG(INFO) << __func__;
        setFingerDown(false);
    }

    void onAcquired(int32_t result, int32_t vendorCode) override {
        LOG(INFO) << __func__ << " result: " << result << " vendorCode: " << vendorCode;
        if (result != kFingerprintAcquiredVendor) {
            setFingerDown(false);
            if (static_cast<AcquiredInfo>(result) == AcquiredInfo::GOOD) {
                set(kFodStatusPath, 0);
            }
        } else if (vendorCode == 21 || vendorCode == 23) {
            set(kFodStatusPath, 1);
        } else if (vendorCode == 44) {
            setFingerDown(false);
        }
    }

    void cancel() override {
        LOG(INFO) << __func__;
        setFingerDown(false);
        set(kFodStatusPath, 0);
    }

  private:
    void setFingerDown(bool pressed) {
        mDevice->extCmd(mDevice, kCommandNit, pressed ? kParamNitFod : kParamNitNone);
        set(kDispParamPath, pressed ? kLocalHbmOn : kLocalHbmOff);
        mDevice->extCmd(mDevice, kCommandFodPressStatus,
                        pressed ? kParamFodPressed : kParamFodReleased);
    }

    fingerprint_device_t* mDevice = nullptr;
};

static UdfpsHandler* create() {
    return new XiaomiManetUdfpsHandler();
}

static void destroy(UdfpsHandler* handler) {
    delete handler;
}

extern "C" UdfpsHandlerFactory UDFPS_HANDLER_FACTORY = {
        .create = create,
        .destroy = destroy,
};
