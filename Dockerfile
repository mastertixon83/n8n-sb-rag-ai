FROM n8nio/n8n:latest

USER root
RUN apk add --no-cache ffmpeg

USER node
WORKDIR /home/node
RUN npm install \
    @langchain/community \
    @supabase/supabase-js \
    @langchain/openai