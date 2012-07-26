#!/bin/bash
rm cloudblaze.tar.gz
tar -hcvzf  cloudblaze.tar.gz --exclude="cloudblaze/blazeweb/lib" --exclude=".git" * 

