
#
# Copyright (C) 2023 The Android Open Source Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Sensors
# This must precede the common tree so the manet-specific multihal list wins
# over the stock copy rule for the same destination.
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/sensors/hals.conf:$(TARGET_COPY_OUT_VENDOR)/etc/sensors/hals.conf \
    $(LOCAL_PATH)/configs/display/spr_cfg_xiaomi_n11u_42_02_0a_cmd_mode_dsc_dsi_panel.xml:$(TARGET_COPY_OUT_VENDOR)/etc/spr_cfg_xiaomi_n11u_42_02_0a_cmd_mode_dsc_dsi_panel.xml \
    $(LOCAL_PATH)/configs/init/init.manet-display.rc:$(TARGET_COPY_OUT_ODM)/etc/init/init.manet-display.rc

# Use manet's QSSI policy instead of the generic common policy.
SM8650_AUDIO_POLICY_QSSI := $(LOCAL_PATH)/configs/audio/audio_policy_configuration_pineapple_qssi.xml

# Inherit from sm8650-common
$(call inherit-product, device/xiaomi/sm8650-common/common.mk)

# Fingerprint
# The Goodix HAL uses Xiaomi's extended v2 fingerprint_device_t ABI.
$(call soong_config_set,XIAOMI_BIOMETRICS_FINGERPRINT,IMPL_VER,V2)

# Get non-open-source specific aspects
$(call inherit-product, vendor/xiaomi/manet/manet-vendor.mk)

PRODUCT_BROKEN_VERIFY_USES_LIBRARIES := true

# Wrap the stock QSH SubHAL so AOSP can register Xiaomi's FOD detector as a
# one-shot wake-up sensor.
PRODUCT_PACKAGES += \
    sensors.qsh.manet \
    libudfpshandler.manet

# Fingerprint
# /dev/goodix_fp is created 0600 root:root, but the Goodix HAL runs as user
# "system" and crashes (null device, then SIGSEGV) when it cannot open the node.
# The node permission is fixed via the shared ueventd rule in sm8650-common
# (ueventd.qcom.rc), which applies when the driver probes the node late in boot.

# Audio
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/audio/mixer_paths_pineapple_mtp.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio/sku_pineapple/mixer_paths_pineapple_mtp.xml \
    $(LOCAL_PATH)/configs/audio/resourcemanager_pineapple_mtp_vendor.xml:$(TARGET_COPY_OUT_VENDOR)/etc/audio/sku_pineapple/resourcemanager_pineapple_mtp.xml \
    hardware/qcom-caf/sm8650/audio/primary-hal/configs/common/bluetooth_qti_hearing_aid_audio_policy_configuration.xml:$(TARGET_COPY_OUT_VENDOR)/etc/bluetooth_qti_hearing_aid_audio_policy_configuration.xml \
    $(LOCAL_PATH)/configs/audio/mixer_paths_pineapple_mtp.xml:$(TARGET_COPY_OUT_ODM)/etc/audio/sku_pineapple/mixer_paths_pineapple_mtp.xml \
    $(LOCAL_PATH)/configs/audio/resourcemanager_pineapple_mtp.xml:$(TARGET_COPY_OUT_ODM)/etc/audio/sku_pineapple/resourcemanager_pineapple_mtp.xml \
    $(LOCAL_PATH)/configs/audio/mixer_paths_overlay_static.xml:$(TARGET_COPY_OUT_ODM)/etc/audio/sku_pineapple/mixer_paths_overlay_static.xml \
    $(LOCAL_PATH)/configs/audio/mixer_paths_overlay_dynamic.xml:$(TARGET_COPY_OUT_ODM)/etc/audio/sku_pineapple/mixer_paths_overlay_dynamic.xml \
    $(LOCAL_PATH)/configs/audio/audio-test-config:$(TARGET_COPY_OUT_ODM)/etc/audio-test-config

# QSPA selects the Qualcomm IMS/QTI telephony APK set through read-only boot
# properties. Keep the default profile explicitly selected for this device.
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/qspa/qspa_system.rc:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/init/qspa_system.rc \
    $(LOCAL_PATH)/configs/qspa/qspa_default.rc:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/qspa/qspa_default.rc

# Soong namespaces
PRODUCT_SOONG_NAMESPACES += \
    $(LOCAL_PATH)

# Overlays
PRODUCT_PACKAGES += \
    FrameworksResManet \
    NfcResManet \
    SecureElementResTarget \
    SettingsOverlayManet \
    SettingsProviderResManet \
    SystemUIResManet \
    WifiResManet
