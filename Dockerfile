# Dockerfile для кастомного образа n8n с Langchain зависимостями
FROM n8nio/n8n:latest

# Устанавливаем необходимые пакеты npm
# `--unsafe-perm` может понадобиться из-за особенностей user в образе n8n.
# https://docs.n8n.io/hosting/installation/docker/#custom-npm-packages
RUN npm install --unsafe-perm \
    @langchain/community \
    @supabase/supabase-js \
    @langchain/openai