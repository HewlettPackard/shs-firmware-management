%define product slingshot
%define component firmware-management
%define component_prefix /opt/%{product}/%{component}
%define _build_id %{version}-%{release}
%define _prefix %{component_prefix}/%{_build_id}

%define firmware_search_dir /opt/slingshot/firmware
%define mlnx_firmware_dir %{firmware_search_dir}/mellanox/%{_build_id}
%define img_dir %{mlnx_firmware_dir}/images


Name: %{product}-%{component}
Version: 2.0.11
Release: %(echo ${BUILD_METADATA})
Group: System Environment/Libraries
License: BSD
Url: http://www.hpe.com
Source: %{name}-%{version}.tar.gz
Vendor: Hewlett Packard Enterprise Company
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
Packager: Hewlett Packard Enterprise Company
Summary: Firmware management tools for Slingshot
Obsoletes: cray-shasta-mlnx-firmware
Distribution: Slingshot

%description
Support software and images for Mellanox hardware on Cray Shasta images

%package -n %{product}-firmware-mellanox
Summary: Firmware images and software for Mellanox hardware used in Slingshot configurations
Requires: mstflint
Requires: mft

%description -n %{product}-firmware-mellanox
Firmware binaries and configuration for Mellanox adapters in Slingshot

%prep
%setup -q -n %{name}-%{version}

%build

%install
# install slingshot-firmware-mellanox
mkdir -p %{buildroot}/%{mlnx_firmware_dir}/bin
for each in $(ls bin/mellanox/*) ; do
    sed -e "s:@CONFIG_DIR@:%{mlnx_firmware_dir}/firmware:g" \
        -e "s:@IMG_DIR@:%{img_dir}:g" \
        -i $each
    install -m 0700 -t %{buildroot}/%{mlnx_firmware_dir}/bin $each
done

for device in $(ls firmware) ; do
    mkdir -p %{buildroot}/%{mlnx_firmware_dir}/firmware/${device}
    install -m 0600 -t %{buildroot}/%{mlnx_firmware_dir}/firmware/${device} firmware/${device}/*
done

# install slingshot-firmware-management
mkdir -p %{buildroot}/%{_prefix}/bin
install -m 0700 -t %{buildroot}/%{_prefix}/bin bin/slingshot-firmware
sed -i -e 's/VERSION=dev-master/VERSION=%{version}/g' %{buildroot}/%{_prefix}/bin/slingshot-firmware

%clean
rm -rf %{buildroot}

%post
ln -sf %{_prefix} %{component_prefix}/default
ln -sf %{component_prefix}/default/bin/slingshot-firmware /usr/bin/slingshot-firmware

%postun
rm -rf %{_prefix}
SH_PREFIX=%{_prefix}
SH_PREFIX_BASE=${SH_PREFIX%/%{_build_id}}
# replace version number with default
SH_PREFIX_DEFAULT=${SH_PREFIX_BASE}/default
if [ "$(ls -l ${SH_PREFIX_DEFAULT} 2>/dev/null | sed 's#.*/##')" == "%{_build_id}" ]; then
    # if this is the active instance of the package then we delete the default symlinks
    rm -f ${SH_PREFIX_DEFAULT}
    # if previous versions exist then find the latest
    SH_LAST=$(ls -r ${SH_PREFIX_BASE} | grep -E '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
    if [ ${#SH_LAST} -eq 0 ]; then
        # This is the last instance of the package so we delete all the symlinks
        rm -f /usr/bin/slingshot-fw-update
        # delete the directories (if empty)
        rmdir ${SH_PREFIX_BASE} 2>/dev/null || true
        rmdir ${SH_PREFIX_BASE%/%{name}} 2>/dev/null || true
    else
        # a previous version exists, make previous active with default symlink
        ln -s ${SH_PREFIX_BASE}/${SH_LAST} ${SH_PREFIX_DEFAULT}
    fi
fi

%post -n %{product}-firmware-mellanox
mkdir -p %{img_dir}
for directory in $(ls %{mlnx_firmware_dir}/firmware | egrep "MT_|CRAY") ; do
    ln -s $(ls %{mlnx_firmware_dir}/firmware/$directory/*.bin) %{img_dir}/$directory.bin
done
ln -sf %{mlnx_firmware_dir} %{firmware_search_dir}/mellanox/default

%postun -n %{product}-firmware-mellanox
rm -rf %{mlnx_firmware_dir}

SH_PREFIX=%{mlnx_firmware_dir}
SH_PREFIX_BASE=${SH_PREFIX%/%{_build_id}}

# replace version number with default
SH_PREFIX_DEFAULT=${SH_PREFIX_BASE}/default
if [ "$(ls -l ${SH_PREFIX_DEFAULT} 2>/dev/null | sed 's#.*/##')" == "%{_build_id}" ]; then
    # if this is the active instance of the package then we delete the default symlinks
    rm -f ${SH_PREFIX_DEFAULT}

    # if previous versions exist then find the latest
    SH_LAST=$(ls -r ${SH_PREFIX_BASE} | grep -E '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
    if [ ${#SH_LAST} -eq 0 ]; then
        # delete the directories (if empty)
        rmdir ${SH_PREFIX_BASE} 2>/dev/null || true
        rmdir ${SH_PREFIX_BASE%/%{name}} 2>/dev/null || true
    else
        # a previous version exists, make previous active with default symlink
        ln -s ${SH_PREFIX_BASE}/${SH_LAST} ${SH_PREFIX_DEFAULT}
    fi
fi

%files
%defattr(-,root,root,-)
%dir %{_prefix}/bin
%{_prefix}/bin/slingshot-firmware

%files -n %{product}-firmware-mellanox
%defattr(-,root,root,-)
%dir %{mlnx_firmware_dir}
%dir %{mlnx_firmware_dir}/bin
%dir %{mlnx_firmware_dir}/firmware
%{mlnx_firmware_dir}/firmware/**/*
%{mlnx_firmware_dir}/bin/init
%{mlnx_firmware_dir}/bin/discover
%{mlnx_firmware_dir}/bin/query
%{mlnx_firmware_dir}/bin/update_firmware
%{mlnx_firmware_dir}/bin/apply_config
%{mlnx_firmware_dir}/bin/cleanup
%{mlnx_firmware_dir}/bin/common.sh
%doc COPYING
%changelog
