#
# Copyright (C) 2023 The Android Open Source Project
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/xiaomi/manet
KERNEL_PATH := $(DEVICE_PATH)-kernel
# Inherit from sm8650-common
include device/xiaomi/sm8650-common/BoardConfigCommon.mk

# Audio
DEVICE_MANIFEST_PINEAPPLE_FILES += \
    $(DEVICE_PATH)/configs/vintf/manifest_audio.xml

# GNSS
DEVICE_MANIFEST_PINEAPPLE_FILES += \
    $(DEVICE_PATH)/configs/vintf/manifest_gnss.xml

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
TARGET_ODM_PROP += $(DEVICE_PATH)/configs/properties/odm.prop
TARGET_SYSTEM_PROP += $(DEVICE_PATH)/configs/properties/system.prop

# SEPolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor
BOARD_ODM_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/odm
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/system_ext/private

# Inherit from the proprietary version
include vendor/xiaomi/manet/BoardConfigVendor.mk
