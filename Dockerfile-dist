#
# Container for Driver
#
# Expects the following environment variables:
# Crossbar settings:
# CROSSBAR_HOST (default 0.0.0.0)
# CROSSBAR_PORT (default 8080)
# Ser2net (bridge between serial port and TCP for Smoothie)
# SMOOTHIE_HOST (default 0.0.0.0)
# SMOOTHIE_PORT (defaults 3333)
#
FROM common

COPY root.tar.gz root.tar.gz
RUN tar -xvzf root.tar.gz -C / && rm root.tar.gz
WORKDIR /home/sandbox-driver-master

ENTRYPOINT ["python3", "driver/driver_client.py"]