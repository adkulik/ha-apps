ARG BUILD_FROM
FROM ${BUILD_FROM}

# Thin Home Assistant wrapper: translate /data/options.json into the
# environment variables the upstream server reads, then exec it as PID 1.
COPY run.py /ha/run.py

CMD ["python", "/ha/run.py"]
