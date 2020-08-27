echo "Waiting for postgres..."
    while ! netcat -z 127.0.0.1 5432; do
      sleep 0.1
    done
echo "Postgres started"
