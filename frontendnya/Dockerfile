FROM python:3.10

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 3000
CMD ["streamlit", "run", "frontend.py", "--server.port=3000", "--server.address=0.0.0.0"]
