FROM python:3.11-slim

WORKDIR /app

# Skip the heavy system updates for now to see if we can bypass the network error
# Just copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8505

ENTRYPOINT ["streamlit", "run", "streamlit_app_v10.py", "--server.port=8505", "--server.address=0.0.0.0"]