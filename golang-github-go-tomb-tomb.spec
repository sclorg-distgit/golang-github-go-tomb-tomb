%{?scl:%scl_package %{name}}

%if 0%{?fedora} || 0%{?rhel} == 6|| 0%{?rhel} == 7
%global with_devel 1
%global with_bundled 0
%global with_debug 0
%global with_check 1
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         go-tomb
%global repo            tomb
# https://github.com/go-tomb/tomb
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     gopkg.in/tomb.v2
%global commit          14b3d72120e8d10ea6e6b7f87f7175734b1faab8
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global import_path_sec gopkg.in/v2/tomb

Name:           %{?scl_prefix}golang-%{provider}-%{project}-%{repo}
Version:        0
Release:        0.4.git%{shortcommit}%{?dist}
Summary:        Helps with clean goroutine termination in the Go language
License:        BSD
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
%endif

Provides:      %{?scl_prefix}golang(%{import_path}) = %{version}-%{release}
Provides:      %{?scl_prefix}golang(%{import_path_sec}) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build
%{?scl:scl enable %{scl} - << "EOF"}

%{?scl:EOF}
%install
%{?scl:scl enable %{scl} - << "EOF"}
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
install -d -p %{buildroot}/%{gopath}/src/%{import_path_sec}/
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path_sec}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path_sec}/$file
    echo "%%{gopath}/src/%%{import_path_sec}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%if 0%{?with_devel}
olddir=$(pwd)
pushd %{buildroot}/%{gopath}/src/%{import_path}
for file in $(find . -type d) ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$file" >> ${olddir}/devel.file-list
done
popd
echo "%%dir %%{gopath}/src/gopkg.in" >> devel.file-list

sort -u -o devel.file-list devel.file-list
%endif

%if 0%{?with_devel}
olddir=$(pwd)
pushd %{buildroot}/%{gopath}/src/%{import_path_sec}
for file in $(find . -type d) ; do
    echo "%%dir %%{gopath}/src/%%{import_path_sec}/$file" >> ${olddir}/devel.file-list
done
popd
echo "%%dir %%{gopath}/src/gopkg.in/v2" >> devel.file-list
echo "%%dir %%{gopath}/src/gopkg.in" >> devel.file-list

sort -u -o devel.file-list devel.file-list
%endif

%{?scl:EOF}
%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

%gotest %{import_path}
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%doc README.md
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%files unit-test -f unit-test.file-list
%license LICENSE
%doc README.md
%endif

%changelog
* Wed Feb 3 2016 Marek Skalicky <mskalick@redhat.com> - 0-0.4.git14b3d72
- Fixed directory ownership

* Sat Sep 12 2015 jchaloup <jchaloup@redhat.com> - 0-0.3.git14b3d72
- Update to spec-2.1
  related: #1249041

* Fri Jul 31 2015 jchaloup <jchaloup@redhat.com> - 0-0.2.git14b3d72
- Update spec file to spec-2.0
  resolves: #1249041

* Mon Jun 15 2015 Marek Skalický <mskalick@redhat.com> - 0-0.1.git14b3d72
- First package for Fedora
  resolves: #1232221

