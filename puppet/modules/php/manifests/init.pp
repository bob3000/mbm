class php {
    package { "php5": }
    package { "php5-curl": }

    file { "/var/www/html/oauth":
        ensure => "link",
        target => "/home/vagrant/mbm/token_procurer",
        require => Package['php5'],
    }

    file { "/etc/php5/cli/php.ini":
        source => "puppet:///modules/php/php.ini",
        require => Package['php5'],
    }

    file { "/etc/php5/apache2/php.ini":
        source => "puppet:///modules/php/php.ini",
        require => Package['php5'],
    }

    file { "/home/vagrant/mbm/token_procurer/vendor":
        ensure => "link",
        target => "/home/vagrant/mbm/token_procurer/ohmy-auth/vendor",
    }

}
