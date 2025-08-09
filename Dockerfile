FROM n8nio/n8n:latest

# Устанавливаем пакеты в /home/node/.n8n для пользователя node
# docker compose build --no-cache
WORKDIR /home/node
USER node
RUN npm install \
    @langchain/community \
    @supabase/supabase-js \
    @langchain/openai