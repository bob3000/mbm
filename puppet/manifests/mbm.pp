Exec {
    path => "/bin:/usr/bin:/sbin:/usr/sbin",
    user => "root",
    logoutput => on_failure,
}

Package {
    ensure => "latest",
    require => Exec["update"],
}

exec { "update":
    command => "apt-get update && touch /root/.updated",
    creates => "/root/.updated",
}

file { "/home/vagrant/.bash_login":
    content => "export LC_ALL=C
    alias mbm='PYTHONPATH=/home/vagrant/mbm/ python3 -m mbm'
    cd /home/vagrant/mbm
    ",
}

file { "/var/www/html/oauth":
    ensure => "link",
    target => "/home/vagrant/mbm/token_procurer",
}

# basic dependencies
package { "python3": }
package { "python-dev": }
package { "python3-setuptools": }
package { "pep8": }
package { "python3-flake8": }

# php
package { "php5": }
package { "php5-curl": }

# install coverage
exec { "easy_install3 coverage":
    creates => "/usr/local/bin/coverage3",
    require => [
        Package["python-dev"],
    Package["python3"],
    Package["python3-setuptools"],
    ]
}
