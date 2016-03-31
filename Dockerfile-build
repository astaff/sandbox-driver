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
FROM common-build

WORKDIR /home
RUN wget https://github.com/OpenTrons/sandbox-driver/archive/master.zip -O temp.zip && unzip temp.zip && rm temp.zip
WORKDIR /home/sandbox-driver-master
COPY patch.diff driver/patch.diff
COPY smoothie.diff driver/smoothie.diff
RUN cd driver \
    && patch driver_client.py < patch.diff \
    && patch smoothie_driver.py < smoothie.diff \
    && pip3 install autobahn==0.10.3

RUN rm -rf /var/cache/apk/*
ENTRYPOINT ["tar", "-cvz", "/usr/lib/python3.5/site-packages/", "/home/sandbox-driver-master"]
# ENTRYPOINT ["python3","driver/driver_client.py"]
