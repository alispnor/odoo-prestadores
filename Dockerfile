FROM odoo:17.0

USER root

SHELL ["/bin/bash", "-c"]

RUN set -euxo pipefail \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /var/lib/apt/lists/partial \
  && apt-get -o Acquire::ForceIPv4=true update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates gnupg dirmngr gettext-base \
  && rm -rf /var/lib/apt/lists/*

USER odoo