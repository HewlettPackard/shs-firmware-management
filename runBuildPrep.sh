#!/bin/bash
#
# Copyright 2021 Hewlett Packard Enterprise Development LP. All rights reserved.
#

PACKAGES="wget"
if command -v yum > /dev/null; then
    yum install -y $PACKAGES
elif command -v zypper > /dev/null; then
    zypper -n install $PACKAGES
else
    "Unsupported package manager or package manager not found -- installing nothing"
fi

for each in firmware/* ; do 
	if [[ -d $each ]] ; then
		pushd $each 
		for entry in $(cat manifest) ; do
            wget https://arti.hpc.amslabs.hpecorp.net/artifactory/mellanox-third-party-stable-local/$entry
		done
		popd
	fi
done

rm $(find . -name '*.bin.*')


if [[ -v SHS_NEW_BUILD_SYSTEM ]]; then
  . ${CE_INCLUDE_PATH}/load.sh

  replace_release_metadata "slingshot-firmware-management.spec"
else
set -x
BRANCH=`git branch --show-current || git rev-parse --abbrev-ref HEAD`

if [ -d hpc-shs-version ]; then
    git -C hpc-shs-version pull
else
    if [[ -n "${SHS_LOCAL_BUILD}" ]]; then
        git clone git@github.hpe.com:hpe/hpc-shs-version.git
    else
    	git clone https://$HPE_GITHUB_TOKEN@github.hpe.com/hpe/hpc-shs-version.git
    fi
fi

. hpc-shs-version/scripts/get-shs-version.sh
. hpc-shs-version/scripts/get-shs-label.sh

PRODUCT_VERSION=$(get_shs_version)
PRODUCT_LABEL=$(get_shs_label)

sed -i "s/Release:.*/Release: ${PRODUCT_LABEL}${PRODUCT_VERSION}_%(echo \\\${BUILD_METADATA:-1})/g" slingshot-firmware-management.spec
fi
