#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import extract_utils.tools
from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixup_remove_arch_suffix,
    lib_fixups,
    lib_fixups_user_type,
    libs_clang_rt_ubsan,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/xiaomi/manet',
    'device/xiaomi/sm8650-common',
    'hardware/qcom-caf/wlan',
    'hardware/qcom-caf/sm8650',
    'hardware/xiaomi',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/dataservices',
]

def blob_fixup_gralloc_029(ctx, file, file_path, *args, **kwargs):
    with open(file_path, 'rb') as f:
        data = bytearray(f.read())
    data[0x7ceb + 0x19] = 0xb5
    with open(file_path, 'wb') as f:
        f.write(data)

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}-{partition}' if partition == 'vendor' else None

def lib_fixup_system_ext_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}-system_ext' if partition == 'system_ext' else None

def lib_fixup_system_ext_protobuf(lib: str, partition: str, *args, **kwargs):
    return 'libprotobuf-cpp-full-21.7' if partition == 'system_ext' else None

lib_fixups: lib_fixups_user_type = {
    # UBSan-instrumented blobs link against the arch-specific clang runtime,
    # while the Soong module is called libclang_rt.ubsan_standalone
    libs_clang_rt_ubsan: lib_fixup_remove_arch_suffix,
    (
        'android.hardware.graphics.composer3-V1-ndk',
        'android.hardware.graphics.allocator-V1-ndk',
        'android.hardware.graphics.composer3-V2-ndk',
        'libmilut',
        'libmips',
        'libmisr',
        'libagmmixer',
        'vendor.qti.hardware.display.composer3-V1-ndk',
    ): lib_fixup_remove,
    (
        'vendor.qti.hardware.qccsyshal@1.0',
        'vendor.qti.hardware.qccsyshal@1.1',
        'vendor.qti.hardware.qccsyshal@1.2',
        'vendor.qti.qccvndhal_aidl-V1-ndk',
    ): lib_fixup_system_ext_suffix,
    'libprotobuf-cpp-full': lib_fixup_system_ext_protobuf,
    (
        'vendor.qti.diaghal@1.0',
        'vendor.qti.imsrtpservice@3.0',
        'vendor.qti.imsrtpservice@3.1',
        'vendor.qti.ImsRtpService-V1-ndk',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'vendor/lib64/libar-pal.so': blob_fixup()
        .replace_needed('libaudioroute.so', 'libaudioroute-v34.so')
        .replace_needed('liblx-osal.so', 'liblx-osal-manet.so'),
    'vendor/lib64/liblx-osal-manet.so': blob_fixup()
        .fix_soname(),
    (
        'system_ext/lib/vendor.qti.hardware.qccsyshal@1.2-halimpl.so',
        'system_ext/lib64/vendor.qti.hardware.qccsyshal@1.2-halimpl.so',
    ): blob_fixup()
        .replace_needed('libprotobuf-cpp-full.so', 'libprotobuf-cpp-full-21.7.so'),
    (
        'odm/etc/camera/enhance_motiontuning.xml',
        'odm/etc/camera/night_motiontuning.xml',
        'odm/etc/camera/motiontuning.xml'
    ): blob_fixup()
        .regex_replace('xml=version', 'xml version'),
    (
        'odm/lib64/libcamxcommonutils.so',
        'vendor/lib64/libcameraopt.so',
    ): blob_fixup()
        .add_needed('libprocessgroup_shim.so'),
    # Preserve the OTA allocator dependency set.  Rewriting V1 to V2 here
    # corrupts pipeline teardown under the Lineage camera provider.
    (
        'odm/lib64/hw/com.qti.chi.override.so',
        'odm/lib64/libchifeature2.so',
    ): blob_fixup()
        .add_needed('libprocessgroup_shim.so'),
    # The OTA CamX teardown double-frees this descriptor under Aperture.
    # Keep the pointer clear but skip the second delete; the provider is
    # short-lived and leaking this descriptor is safer than aborting.
    'odm/lib64/hw/camera.qcom.so': blob_fixup()
        .add_needed('libprocessgroup_shim.so')
        .binary_regex_replace(
            b'\x30\x56\x30\x94',
            b'\x1f\x20\x03\xd5',
        ),
    # Avoid the vendor smooth-switch teardown race on the Lineage provider.
    # Keep multi-camera enabled: disabling it removes the ultrawide physical
    # camera from the logical camera controls on manet.
    'odm/etc/camera/camxoverridesettings.txt': blob_fixup()
        .regex_replace(
            'enableEarlyPipelineActivate=TRUE',
            'enableEarlyPipelineActivate=FALSE',
        )
        .regex_replace(
            'isSwitchAnimationSupported=TRUE',
            'isSwitchAnimationSupported=FALSE',
        )
        .regex_replace(
            'multiCameraEnable=FALSE',
            'multiCameraEnable=TRUE',
        )
        .regex_replace(
            'sessionMaxFlushWaitTime=1000',
            'sessionMaxFlushWaitTime=5000',
        ),
    'odm/lib64/com.qti.feature2.anchorsync.so': blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so'),
    'odm/lib64/camera/plugins/com.xiaomi.plugin.anchor.so': blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so'),
    'odm/lib64/hw/camera.xiaomi.so': blob_fixup()
        .add_needed('libprocessgroup_shim.so')
        .replace_needed('libui.so', 'libui-v34.so')
        .binary_regex_replace(
            b'\x00\x20\x80\x52\xf9\x03\x05\xaa',
            b'\x00\xa6\x81\x52\xf9\x03\x05\xaa',
        )
        .binary_regex_replace(
            b'\x00\x20\x80\x52\x08\x15\x40\xf9',
            b'\x00\xa6\x81\x52\x08\x15\x40\xf9',
        )
        .binary_regex_replace(
            b'\x00\x20\x80\x52\xf5\x03\x05\xaa',
            b'\x00\xa6\x81\x52\xf5\x03\x05\xaa',
        )
        .binary_regex_replace(
            b'\x00\x20\x80\x52\xf5\x03\x02\xaa',
            b'\x00\xa6\x81\x52\xf5\x03\x02\xaa',
        ),
    'system_ext/framework/mirilhook.jar': blob_fixup()
        .apktool_patch('blob-patches/mirilhook.patch'),
    (
        'vendor/bin/hw/vendor.qti.media.c2@1.0-service',
        'vendor/bin/hw/vendor.dolby.media.c2@1.0-service',
        'vendor/bin/hw/vendor.qti.media.c2audio@1.0-service',
    ): blob_fixup()
        .add_needed('libshim.so'),
    (
        'vendor/etc/media_codecs_pinaepple.xml',
        'vendor/etc/media_codecs_pinaepple_vendor.xml',
    ): blob_fixup()
        .regex_replace(
            '.*media_codecs_(google_audio|google_c2|google_telephony|google_video|vendor_audio).*\\n',
            '',
        ),
    'vendor/lib64/vendor.libdpmframework.so': blob_fixup()
        .add_needed('libhidlbase_shim.so')
        .add_needed('libbinder_shim.so'),
    (
        'vendor/lib64/libqcc_sdk.so',
        'vendor/lib64/libqms_xiaomi.so',
        'vendor/lib64/libqms_client.so',
        'vendor/bin/qcc-vendor',
        'vendor/bin/xtra-daemon',
        'vendor/bin/qms',
        'vendor/bin/cnd',
    ): blob_fixup()
        .add_needed('libbinder_shim.so'),
    'vendor/lib64/libqcodec2_core.so': blob_fixup()
        .add_needed('libcodec2_shim.so'),
    (
        'vendor.qti.hardware.display.composer-service',
        'vendor/lib64/libsnapdragoncolor-manager.so',
        'vendor/lib64/libdpps.so',
        'vendor/bin/poweropt-service',
    ): blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2_1.so'),
    (
        'vendor/lib64/libVoiceSdk.so',
        'vendor/lib64/libcapiv2uvvendor.so',
        'vendor/lib64/liblistensoundmodel2vendor.so',
    ): blob_fixup()
        .replace_needed('libtensorflowlite_c.so', 'libtensorflowlite_c_vendor.so'),
    'vendor/lib64/hw/audio.primary.pineapple.so': blob_fixup()
        .add_needed('libar_gpr_shim.so'),
    'vendor/lib64/libxlog.so': blob_fixup()
        .replace_needed(
            'vendor.xiaomi.hardware.mediaeventgatherservice-V1-ndk.so',
            'vendor.xiaomi.hardware.mediaeventgatherservice-V1-ndk_vendor.so',
        ),
    'vendor/lib64/libgrallocutils.so': blob_fixup()
        .call(blob_fixup_gralloc_029),
}

module = ExtractUtilsModule(
    'manet',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    check_elf=True,
    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
