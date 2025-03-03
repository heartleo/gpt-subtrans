FROM python:3.12-bookworm AS builder

WORKDIR /app
COPY requirements.txt /app
ENV PATH="/app/envsubtrans/bin:$PATH"
RUN python -m venv --copies /app/envsubtrans envsubtrans
RUN envsubtrans/bin/pip install --upgrade -r requirements.txt
COPY . .
RUN envsubtrans/bin/pip install openai && scripts/generate-cmd.sh gpt-subtrans
#RUN pwd && ls -al

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app /app
RUN pwd && ls -al
ENV PATH="/app/envsubtrans/bin:$PATH"
CMD ["python","scripts/gpt-subtrans.py"]