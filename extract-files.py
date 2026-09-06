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
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/xiaomi/sm8650-common',
    'hardware/qcom-caf/sm8650',
    'hardware/xiaomi',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/xiaomi/sm8650-common',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}-{partition}' if partition == 'vendor' else None

def lib_fixup_system_ext_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}-system_ext' if partition == 'system_ext' else None

def lib_fixup_system_ext_protobuf(lib: str, partition: str, *args, **kwargs):
    return 'libprotobuf-cpp-full-21.7' if partition == 'system_ext' else None

lib_fixups: lib_fixups_user_type = {
    (
        'android.hardware.graphics.composer3-V1-ndk',
        'android.hardware.graphics.allocator-V1-ndk',
    ): lib_fixup_remove,
    (
        'vendor.qti.hardware.qccsyshal@1.0',
        'vendor.qti.hardware.qccsyshal@1.1',
        'vendor.qti.hardware.qccsyshal@1.2',
        'vendor.qti.qccvndhal_aidl-V1-ndk',
    ): lib_fixup_system_ext_suffix,
    'libprotobuf-cpp-full': lib_fixup_system_ext_protobuf,
}

camera_allocator_v2_blobs = (
    'odm/lib64/camera/com.qti.actuator.manet_ofilm_ov50d40_dw9800v_tele_actuator.so',
    'odm/lib64/camera/com.qti.actuator.manet_ofilm_ovx8000_gt9764ber_wide_actuator.so',
    'odm/lib64/camera/com.qti.eeprom.manet_ofilm_ov13b10_p24c64e_ultra_eeprom.so',
    'odm/lib64/camera/com.qti.eeprom.manet_ofilm_ov50d40_gt24p128e_tele_eeprom.so',
    'odm/lib64/camera/com.qti.eeprom.manet_ofilm_ovx8000_gt24p128_wide_eeprom.so',
    'odm/lib64/camera/com.qti.eeprom.manet_sunny_ov16a1q_p24c64f_front_eeprom.so',
    'odm/lib64/camera/com.qti.sensor.manet_ofilm_ov13b10_ultra.so',
    'odm/lib64/camera/com.qti.sensor.manet_ofilm_ov50d40_tele.so',
    'odm/lib64/camera/com.qti.sensor.manet_ofilm_ovx8000_wide.so',
    'odm/lib64/camera/com.qti.sensor.manet_sunny_ov16a1q_front.so',
    'odm/lib64/camera/components/com.jigan.node.videobokeh.so',
    'odm/lib64/camera/components/com.mi.node.aiasd.so',
    'odm/lib64/camera/components/com.mi.node.dlengine.so',
    'odm/lib64/camera/components/com.mi.node.mawsaliency.so',
    'odm/lib64/camera/components/com.mi.node.rearvideo.so',
    'odm/lib64/camera/components/com.mi.node.skinbeautifier.so',
    'odm/lib64/camera/components/com.mi.node.videobokeh.so',
    'odm/lib64/camera/components/com.mi.node.videofilter.so',
    'odm/lib64/camera/components/com.mi.node.videonight.so',
    'odm/lib64/camera/components/com.qti.node.aon.so',
    'odm/lib64/camera/components/com.qti.node.depth.so',
    'odm/lib64/camera/components/com.qti.node.depthprovider.so',
    'odm/lib64/camera/components/com.qti.node.dewarp.so',
    'odm/lib64/camera/components/com.qti.node.eisv2.so',
    'odm/lib64/camera/components/com.qti.node.eisv3.so',
    'odm/lib64/camera/components/com.qti.node.evadepth.so',
    'odm/lib64/camera/components/com.qti.node.gme.so',
    'odm/lib64/camera/components/com.qti.node.gyrornn.so',
    'odm/lib64/camera/components/com.qti.node.hdr10pgen.so',
    'odm/lib64/camera/components/com.qti.node.hdr10phist.so',
    'odm/lib64/camera/components/com.qti.node.itofpreprocess.so',
    'odm/lib64/camera/components/com.qti.node.ml.so',
    'odm/lib64/camera/components/com.qti.node.mlinference.so',
    'odm/lib64/camera/components/com.qti.node.pixelstats.so',
    'odm/lib64/camera/components/com.qti.node.seg.so',
    'odm/lib64/camera/components/com.qti.node.swec.so',
    'odm/lib64/camera/components/com.qti.node.swregistration.so',
    'odm/lib64/camera/components/com.qti.node.swvrt.so',
    'odm/lib64/camera/components/com.qti.stats.cnndriver.so',
    'odm/lib64/camera/components/com.xiaomi.node.smooth_transition.so',
    'odm/lib64/camera/components/libcamxevainterface.so',
    'odm/lib64/camera/components/libdepthmapwrapper_itof.so',
    'odm/lib64/camera/components/libdepthmapwrapper_secure.so',
    'odm/lib64/camera/libchxlogicalcameratable.so',
    'odm/lib64/com.qti.chiusecaseselector.so',
    'odm/lib64/com.qti.feature2.afbrckt.so',
    'odm/lib64/com.qti.feature2.demux.so',
    'odm/lib64/com.qti.feature2.derivedoffline.so',
    'odm/lib64/com.qti.feature2.fusion.so',
    'odm/lib64/com.qti.feature2.generic.so',
    'odm/lib64/com.qti.feature2.gs.sm8650.so',
    'odm/lib64/com.qti.feature2.hdr.so',
    'odm/lib64/com.qti.feature2.mcreprocrt.so',
    'odm/lib64/com.qti.feature2.memcpy.so',
    'odm/lib64/com.qti.feature2.metadataserializer.so',
    'odm/lib64/com.qti.feature2.mfsr.so',
    'odm/lib64/com.qti.feature2.ml.so',
    'odm/lib64/com.qti.feature2.mux.so',
    'odm/lib64/com.qti.feature2.offlinestatsregeneration.so',
    'odm/lib64/com.qti.feature2.qcfa.so',
    'odm/lib64/com.qti.feature2.rawhdr.so',
    'odm/lib64/com.qti.feature2.realtimeserializer.so',
    'odm/lib64/com.qti.feature2.rt.so',
    'odm/lib64/com.qti.feature2.rtmcx.so',
    'odm/lib64/com.qti.feature2.serializer.so',
    'odm/lib64/com.qti.feature2.statsregeneration.so',
    'odm/lib64/com.qti.feature2.stub.so',
    'odm/lib64/com.qti.feature2.swmf.so',
    'odm/lib64/hw/camera.qcom.sm8650.so',
    'odm/lib64/hw/com.qti.chi.offline.so',
    'odm/lib64/libcamerapostproc.so',
    'odm/lib64/libcamxhwnodecontext.so',
    'odm/lib64/libcamxifestriping.so',
    'odm/lib64/libcamximageformatutils.so',
    'odm/lib64/libcamxncsdatafactory.so',
    'odm/lib64/libmmcamera_bestats.so',
    'odm/lib64/libmmcamera_cac.so',
    'odm/lib64/libmmcamera_lscv35.so',
    'odm/lib64/libmmcamera_mfnr.so',
    'odm/lib64/libmmcamera_mfnr_t4.so',
    'odm/lib64/libmmcamera_pdpc.so',
    'odm/lib64/vendor.qti.hardware.camera.aon-service-impl.so',
    'odm/lib64/vendor.qti.hardware.camera.offlinecamera-service-impl.so',
    'odm/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so',
    'odm/lib64/com.qti.camx.chiiqutils.so',
    'odm/lib64/libubifocus.so',
    'odm/lib64/com.qualcomm.qti.mcx.usecase.extension.so',
    'odm/lib64/libofflinefeatureintf.so',
    'odm/lib64/libjpege.so',
    'odm/lib64/com.qualcomm.mcx.nonlinearmapper.so',
    'odm/lib64/libtunningmemhook.so',
    'odm/lib64/libtfestriping.so',
    'odm/lib64/libcommonchiutils.so',
    'odm/lib64/libhme.so',
    'odm/lib64/com.qualcomm.mcx.distortionmapper.so',
    'odm/lib64/com.qti.qseeutils.so',
    'odm/lib64/libmctfengine_stub.so',
    'odm/lib64/libmfec.so',
    'odm/lib64/com.qualcomm.mcx.linearmapper.so',
    'odm/lib64/libipebpsstriping170.so',
    'odm/lib64/libipebpsstriping480.so',
    'odm/lib64/libcom.xiaomi.mawutilsold.so',
    'odm/lib64/libopestriping.so',
    'odm/lib64/com.qualcomm.mcx.policy.mfl.so',
    'odm/lib64/libfastmessage.so',
    'odm/lib64/libipebpsstriping.so',
    'odm/lib64/libisphwsetting.so',
)

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
    (
        'odm/lib64/hw/camera.qcom.so',
        'odm/lib64/hw/com.qti.chi.override.so',
        'odm/lib64/libchifeature2.so',
    ): blob_fixup()
        .add_needed('libprocessgroup_shim.so')
        .binary_regex_replace(
            b'android.hardware.graphics.allocator-V1-ndk.so',
            b'android.hardware.graphics.allocator-V2-ndk.so',
        ),
    camera_allocator_v2_blobs: blob_fixup()
        .binary_regex_replace(
            b'android.hardware.graphics.allocator-V1-ndk.so',
            b'android.hardware.graphics.allocator-V2-ndk.so',
        ),
    'odm/lib64/com.qti.feature2.anchorsync.so': blob_fixup()
        .binary_regex_replace(
            b'android.hardware.graphics.allocator-V1-ndk.so',
            b'android.hardware.graphics.allocator-V2-ndk.so',
        )
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
