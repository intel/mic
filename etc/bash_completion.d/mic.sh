# bash completion for mic
#
# Copyright (c) 2013 Intel, Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; version 2 of the License
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place - Suite 330, Boston, MA 02111-1307, USA.

__miccomp_1 ()
{
	local c IFS=$' \t\n'
	for c in $1; do
		c="$c$2"
		case $c in
		--*=*|*.) ;;
		*) c="$c " ;;
		esac
		printf '%s\n' "$c"
	done
}

__miccomp ()
{
	local cur_="${3-$cur}"

	case "$cur_" in
	--*=)
		COMPREPLY=()
		;;
	*)
		local IFS=$'\n'
		COMPREPLY=($(compgen -P "${2-}" \
			-W "$(__miccomp_1 "${1-}" "${4-}")" \
			-- "$cur_"))
		;;
	esac
}

__mic_find_on_cmdline ()
{
    local word subcommand c=1
    while [ $c -lt $cword ]; do
        word="${words[c]}"
        for subcommand in $1; do
            if [ "$subcommand" = "$word" ]; then
                echo "$subcommand"
                return
            fi
        done
        let c++
    done
}

__mic_expand_alias ()
{
    case ${subcommand} in
        cr*) subcommand="create" ;;
        ch*) subcommand="chroot" ;;
        c*v*) subcommand="convert" ;;
    esac
}

__mic_complete_opt()
{
    fs_exts="
        --include-src
    "
    loop_exts="
        --shrink
        --compress-image=
        --compress-disk-image=
    "
    raw_exts="
        --fstab-entry=
        --generate-bmap
        --compress-image=
        --compress-disk-image=
    "

    keyword="$(__mic_find_on_cmdline "fs loop raw")"
    eval extensions="$"{${keyword}_exts}

    __miccomp "${options} ${extensions}"
}

__mic_complete_val()
{
    _values="
    "
    arch_values="
        ia64
        i686
        i586
        x86_64
        armv5l
        armv6l
        armv7l
        armv7hl
        armv7thl
        armv7nhl
        armv5tel
        armv5tejl
        armv7tnhl
    "
    pkgmgr_values="
        yum
        zypper
    "
    release_values="
        latest
    "
    runtime_values="
        native
        bootstrap
    "
    record_pkgs_values="
        vcs
        name
        content
        license
    "
    fstab_entry_values="
        name
        uuid
    "
    install_pkgs_values="
        source
        debuginfo
        debugsoure
    "
    compress_image_values="
        gz
        bz2
        lzo
    "
    compress_disk_image_values="
        gz
        bz2
        lzo
    "

    declare -F _split_longopt &>/dev/null && _split_longopt

    prev_=${prev##--}
    eval values="$"{${prev_//-/_}_values}
    __miccomp "${values}"
}

__mic_complete_arg()
{
    local before c=$((cword-1))
    while [[ $c -gt 0 ]]; do
        before=${words[c]} && [[ "$before" != -* ]] && break;
        let c--
    done

    case ${subcommand},${before} in
        cr*,cr*)
            __miccomp "${arguments}"
            return 0
            ;;
        c*v*,fs|loop|raw|livecd|liveusb)
            __miccomp "${arguments}"
            return 0
            ;;
        help,help)
            __miccomp "${arguments}"
            return 0
            ;;
    esac

    return 1
}

__mic ()
{
	if [ -z "$subcommand" ]; then
		case "$cur" in
		-*)
            __miccomp "${options}"
			;;
		*)
            __miccomp "${subcommands}"
            ;;
		esac
	else
        case "$cur" in
        --*=*)
            __mic_complete_val
            ;;
        -*)
            __mic_complete_opt
            ;;
        *)
            __mic_complete_arg || COMPREPLY=()
            ;;
        esac
    fi
}

__mic_main ()
{
    subcommands="
        help
        create
        chroot
        convert
    "
    alias="
        cr
        ch
        cv
    "

    _opts="
        --version
    "
    common_opts="
        --help
        --debug
        --verbose
    "
    create_opts="
        --arch=
        --tmpfs
        --config=
        --pkgmgr=
        --outdir=
        --pack-to=
        --logfile=
        --runtime=
        --release=
        --cachedir=
        --copy-kernel
        --check-pkgs=
        --record-pkgs=
        --install-pkgs=
        --local-pkgs-path=
    "
    convert_opts="
        --shell
    "
    chroot_opts="
        --saveto=
    "
    help_opts="
    "

    _args="
    "
    create_args="
        auto
        fs
        livecd
        liveusb
        loop
        raw
    "
    convert_args="
        fs
        livecd
        liveusb
        loop
        raw
    "
    chroot_args="
    "
    help_args="
        create
        convert
        chroot
    "

    local cur prev words cword
    if declare -F _get_comp_words_by_ref &>/dev/null ; then
        _get_comp_words_by_ref cur prev words cword
    else
        cur=$2 prev=$3 words=("${COMP_WORDS[@]}") cword=$COMP_CWORD
    fi

    local subcommand
    subcommand="$(__mic_find_on_cmdline "$subcommands $alias")"
    __mic_expand_alias

    local options arguments
    eval options="$"{${subcommand}_opts}"\ $"{common_opts}
    eval arguments="$"{${subcommand}_args}

    __mic && return

} &&
complete -F __mic_main -o bashdefault -o default -o nospace mic

# Local variables:
# mode: shell-script
# sh-basic-offset: 4
# sh-indent-comment: t
# indent-tabs-mode: nil
# End:
# ex: ts=4 sw=4 et filetype=sh
