#!/usr/bin/env python3
import os.path
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TOP = f"{SCRIPT_DIR}/../../../.."

PATCHELF_PATH = f"{TOP}/prebuilts/extract-tools/linux-x86/bin/patchelf-0_9"

for vndk_version, libs in {
    "v32": [
        "libhidlbase",
        "libutils",
    ],
    "v33": [
        "libbase",
        "libcrypto",
        "libstagefright_foundation",
        "libutils",
    ],
    "v34": [
        "libaudioroute",
        "libui",
    ],
}.items():
    for lib in libs:
        for arch in ["arm", "arm64"]:
            for path in [
                f"{TOP}/prebuilts/vndk/{vndk_version}/arm64/arch-{arch}-armv8-a/shared/vndk-core/{lib}.so",
                f"{TOP}/prebuilts/vndk/{vndk_version}/arm64/arch-{arch}-armv8-a/shared/vndk-sp/{lib}.so",
            ]:
                if os.path.isfile(path):
                    lib_dest = (
                        f"{SCRIPT_DIR}/{vndk_version}/{arch}/{lib}-{vndk_version}.so"
                    )

                    os.makedirs(os.path.dirname(lib_dest), exist_ok=True)
                    shutil.copyfile(path, lib_dest)
                    shutil.copystat(path, lib_dest)
                    subprocess.run(
                        [
                            PATCHELF_PATH,
                            "--set-soname",
                            os.path.basename(lib_dest),
                            lib_dest,
                        ]
                    )

                    if vndk_version == "v32" and lib == "libutils":
                        subprocess.run(
                            [
                                PATCHELF_PATH,
                                "--add-needed",
                                "libprocessgroup_shim.so",
                                lib_dest,
                            ]
                        )

                    if vndk_version == "v34" and lib == "libui":
                        subprocess.run(
                            [
                                PATCHELF_PATH,
                                "--replace-needed",
                                "android.hardware.graphics.common-V4-ndk.so",
                                "android.hardware.graphics.common-V6-ndk.so",
                                lib_dest,
                            ]
                        )

                    break
            else:
                assert False, f"Failed to find {arch} {lib}"
