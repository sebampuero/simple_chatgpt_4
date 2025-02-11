#!/bin/bash
npm run build

# If the build is successful, upload to S3.
# TODO: develop pipeline to automate deployment to nginx
if [ $? -eq 0 ]; then
    echo "Build successful. Deploying to server..."
    zip -r chatgpt.zip build/
    
    if [ -z "$S3_BUCKET" ]; then
        echo "Error: S3_BUCKET environment variable is not set."
        exit 1
    fi
    
    aws s3 cp chatgpt.zip s3://$S3_BUCKET/chatgpt.zip
    if [ $? -ne 0 ]; then
        echo "Error: Failed to upload to S3."
        exit 1
    fi
else
    echo "Build failed. Deployment aborted."
    exit 1
fi

rm chatgpt.zip