host="kafka"
port=9092

echo "⏳ Esperando a $host:$port..."
while ! nc -z "$host" "$port"; do
  sleep 1
done
echo "✅ $host:$port ya está arriba."
exec "$@"