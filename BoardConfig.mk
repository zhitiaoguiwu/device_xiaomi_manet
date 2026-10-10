#
# Copyright (C) 2023 The Android Open Source Project
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/xiaomi/manet
KERNEL_PATH := $(DEVICE_PATH)-kernel
# Inherit from sm8650-common
include device/xiaomi/sm8650-common/BoardConfigCommon.mk

# Manet uses the partition geometry from its stock firmware, which differs
# from the generic LOS24 pineapple common profile.
BOARD_DTBOIMG_PARTITION_SIZE := 20971520
BOARD_SUPER_PARTITION_SIZE := 9126805504
BOARD_QTI_DYNAMIC_PARTITIONS_SIZE := 9116319744

# Manet's touchscreen driver uses the newer xiaomi-touch ioctl payload. Keep
# the implementation local so the shared common tree remains device-agnostic.
TARGET_POWERHAL_MODE_EXT := $(DEVICE_PATH)/power/power-mode.cpp
SOONG_CONFIG_NAMESPACES += qtipower
SOONG_CONFIG_qtipower += mode_ext_lib
SOONG_CONFIG_qtipower_mode_ext_lib := power_mode_ext

# Expose the Goodix high-touch polling control through the Lineage Xiaomi
# touch service. The stock THP configuration uses 240 Hz normally and 480 Hz
# for the high-touch/game profile.
SOONG_CONFIG_NAMESPACES += XIAOMI_TOUCH
SOONG_CONFIG_XIAOMI_TOUCH += HIGH_TOUCH_POLLING_PATH
SOONG_CONFIG_XIAOMI_TOUCH_HIGH_TOUCH_POLLING_PATH := /sys/devices/platform/goodix_ts.0/switch_report_rate

DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += \
    $(DEVICE_PATH)/configs/vintf/compatibility_matrix.mlipay-hidl.xml

# Display density (matches the stock manet profile)
TARGET_SCREEN_DENSITY := 560

# Dtb/o
BOARD_PREBUILT_DTBOIMAGE := $(KERNEL_PATH)/dtbo.img
BOARD_PREBUILT_DTBIMAGE_DIR := $(KERNEL_PATH)/dtb

TARGET_NO_KERNEL_OVERRIDE := true
TARGET_KERNEL_SOURCE := $(KERNEL_PATH)/kernel-headers
PRODUCT_COPY_FILES += \
	$(KERNEL_PATH)/kernel:kernel

# Kernel modules
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD := $(strip $(shell cat $(KERNEL_PATH)/vendor_ramdisk/modules.load))
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_BLOCKLIST_FILE := $(KERNEL_PATH)/vendor_ramdisk/modules.blocklist

BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD := $(strip $(shell cat $(KERNEL_PATH)/vendor_ramdisk/modules.load.recovery))

BOARD_VENDOR_KERNEL_MODULES_LOAD := $(strip $(shell cat $(KERNEL_PATH)/vendor_dlkm/modules.load))

PRODUCT_COPY_FILES += \
    $(call find-copy-subdir-files,*,$(KERNEL_PATH)/vendor_dlkm/,$(TARGET_COPY_OUT_VENDOR_DLKM)/lib/modules) \
    $(call find-copy-subdir-files,*,$(KERNEL_PATH)/vendor_ramdisk/,$(TARGET_COPY_OUT_VENDOR_RAMDISK)/lib/modules) \
    $(call find-copy-subdir-files,*,$(KERNEL_PATH)/system_dlkm/,$(TARGET_COPY_OUT_SYSTEM_DLKM)/lib/modules/6.1.138-android14-11-g0c3d559bcd85-ab14529422)

# OTA
TARGET_OTA_ASSERT_DEVICE := manet

# Properties
# Keep the property baseline paired with manet's stock audio, Bluetooth and
# modem blobs. Filter only these two common inputs; ODM, product and system_ext
# properties continue to come from the LOS24 shared tree.
TARGET_SYSTEM_PROP := $(filter-out $(COMMON_PATH)/configs/properties/system.prop,$(TARGET_SYSTEM_PROP))
TARGET_VENDOR_PROP := $(filter-out $(COMMON_PATH)/configs/properties/vendor.prop,$(TARGET_VENDOR_PROP))
TARGET_SYSTEM_PROP += $(DEVICE_PATH)/configs/properties/system-common.prop
TARGET_VENDOR_PROP += $(DEVICE_PATH)/configs/properties/vendor-common.prop
TARGET_ODM_PROP += $(DEVICE_PATH)/configs/properties/odm.prop
TARGET_SYSTEM_PROP += $(DEVICE_PATH)/configs/properties/system.prop

# SEPolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor
BOARD_ODM_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/odm
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/system_ext/private

# Inherit from the proprietary version
include vendor/xiaomi/manet/BoardConfigVendor.mk
