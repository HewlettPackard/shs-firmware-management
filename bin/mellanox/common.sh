#!/bin/bash
#
# Copyright 2021 Hewlett Packard Enterprise Development LP
#
# This file should only be sourced.

CONFIG_DIR=@CONFIG_DIR@

function write_to_log() {
    echo "$@" 1>&2
}

function debug() {
    if $DEBUG ; then
        write_to_log "DEBUG: $@"
    fi
}

function info() {
    if $VERBOSE ; then
        write_to_log "INFO: $@"
    fi
}

function warn() {
    write_to_log "WARN: $@"
}

function error() {
    write_to_log "ERROR: $@"
}

function read_mst_data() {
    local device_name=$1
    local found=false

    while read -r device_type device_id pci_id rdma_id net_id numa_region || [[ -n "$line" ]] ; do
        if [[ -z $pci_id ]] ; then
            # skip -- this PCI device couldn't be recognized
            continue
        fi

        for e in $(echo ${net_id} | tr ',' ' ') ; do
            local dev_name=$(echo $e | sed -e 's/^net-//g')
            if [[ "${dev_name}" == "${device_name}" ]] ; then
                found=true
            fi
        done

        if ! $found ; then
            continue
        fi

        # found the device. Is it a managed device?
        local PSID=$(flint -d $device_id query | grep PSID | awk '{print $2}')
        local DEVICE_CONFIG_DIR=$CONFIG_DIR/$PSID

        if [[ ! -d $DEVICE_CONFIG_DIR ]] ; then
            # skip -- this PSID is an unmanaged PSID
            warn "$PSID is not a supported device at this time -- skipping" 1>&2
            warn "list of supported device PSIDs: $(ls $CONFIG_DIR | tr '\n' ' ')" 1>&2

            found=false
            continue
        fi

        if $found ; then
            break
        fi
    done < <(mst status -v | grep "/dev" | grep pciconf)

    if $found ; then
        echo $device_type $device_id $pci_id $rdma_id $net_id $numa_region
    else 
        return 1
    fi
    return 0
}
