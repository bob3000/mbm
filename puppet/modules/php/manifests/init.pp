class php {
    package { "php5": }
    package { "php-pear": }
    package { "php5-dev": }
    package { "libcurl4-openssl-dev": }
    package { "libpcre3-dev": }

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

    exec { "pecl install oauth":
        command => "/usr/bin/pecl install --alldeps OAuth",
        creates => "/usr/share/php/docs/oauth",
        require => [Exec['pear update-channels'],
                    Package['php5-dev'],
                    Package['libcurl4-openssl-dev'],
                    Package['libpcre3-dev'],
                    ],
    }

    file { "/var/www/html/oauth":
        ensure => "link",
        target => "/home/vagrant/mbm/token_procurer",
        require => Package['php5'],
    }

    file { "/etc/php5/cli/php.ini":
        source => "puppet:///modules/php/php.ini",
        require => Exec['pecl install oauth'],
    }

}
