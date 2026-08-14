## Tree

### Docker
waf
│       └── Dockerfile

### src
waf
│       ├── logs
│       │   ├── modsecurity
│       │   │   └── audit.log
│       │   └── nginx
│       │       ├── access.log
│       │       └── error.log
│       ├── modsecurity
│       │   ├── crs-setup.conf
│       │   ├── custom
│       │   │   ├── blacklist.conf
│       │   │   ├── hardening.conf
│       │   │   └── whitelist.conf
│       │   ├── modsecurity.conf.template
│       │   ├── REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
│       │   ├── RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf
│       │   └── unicode.mapping
│       ├── nginx
│       │   ├── conf.d
│       │   │   └── reverse-proxy.conf.template
│       │   └── nginx.conf.template
│       ├── scripts
│       │   ├── entrypoint.sh
│       │   └── ssl-certification-gen.sh
│       └── ssl
│           ├── cert.pem
│           └── key.pem
