FROM ollama/ollama:latest

COPY entrypoint.sh /usr/local/bin/aimodel-entrypoint.sh
RUN chmod +x /usr/local/bin/aimodel-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/aimodel-entrypoint.sh"]
CMD []
