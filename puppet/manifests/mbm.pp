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
    require => Package['php5'],
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
package { "php-pear": }

exec { "pear upgrade":
  command => "/usr/bin/pear upgrade && touch /root/.pear-updated",
  require => Package['php-pear'],
  returns => [ 0, '', ' '],
  creates => "/root/.pear-updated",
}

exec { "pear auto_discover" :
  command => "/usr/bin/pear config-set auto_discover 1 && touch /root/.pear-auto-discover-on",
  require => [Package['php-pear']],
  creates => "/root/.pear-auto-discover-on",
}

exec { "pear update-channels" :
  command => "/usr/bin/pear update-channels && touch /root/.pear-updated-channels",
  require => [Package['php-pear']],
  creates => "/root/.pear-updated-channels",
}

exec {"pear install oauth":
  command => "/usr/bin/pecl install --alldeps OAuth",
  require => Exec['pear update-channels'],
  creates => "/usr/share/php/docs/oauth/examples",
}

# install coverage
exec { "easy_install3 coverage":
    creates => "/usr/local/bin/coverage3",
    require => [
        Package["python-dev"],
    Package["python3"],
    Package["python3-setuptools"],
    ]
}
