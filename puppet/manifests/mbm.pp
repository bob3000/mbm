Exec {
    path => "/bin:/usr/bin:/sbin:/usr/sbin",
    user => "root",
    logoutput => on_failure,
}

Package {
    ensure => "latest",
    require => Exec["update"],
}

class base {
    #include php  ## include php if you want to hack on token_procuer.php
    exec { "update":
        command => "apt-get update && touch /root/.updated",
        creates => "/root/.updated",
    }

    file { "/home/vagrant/.bash_login":
        content => "
        alias mbm='PYTHONPATH=/home/vagrant/mbm/ python3 -m mbm'
        cd /home/vagrant/mbm
        ",
    }

    file { "/usr/share/bash-completion/completions/mbm":
        ensure => "link",
        target => "/home/vagrant/mbm/completion/mbm",
    }

    file { "/usr/share/man/man1/mbm.1":
        ensure => "link",
        target => "/home/vagrant/mbm/man/mbm.1",
    }

    # basic dependencies
    package { "python3": }
    package { "python-dev": }
    package { "python3-setuptools": }
    package { "pep8": }
    package { "python3-flake8": }

    # install coverage
    exec { "easy_install3 coverage":
        creates => "/usr/local/bin/coverage3",
        require => [
            Package["python-dev"],
        Package["python3"],
        Package["python3-setuptools"],
        ]
    }
}

class {"base":}
