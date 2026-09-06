#
# Copyright (C) 2024 The Android Open Source Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit_only.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit some common Lineage stuff.
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Inherit from manet device.
$(call inherit-product, device/xiaomi/manet/device.mk)

## Device identifier
PRODUCT_DEVICE := manet
PRODUCT_NAME := lineage_manet
PRODUCT_BRAND := Redmi
PRODUCT_MODEL := 23117RK66C
PRODUCT_MANUFACTURER := Xiaomi

PRODUCT_BUILD_PROP_OVERRIDES += \
    BuildFingerprint=Redmi/manet/manet:14/UKQ1.240624.001/OS3.0.305.0.WNMCNXM:user/release-keys

# GMS
PRODUCT_GMS_CLIENTID_BASE := android-xiaomi
