# Haystack Pipeline Installation:
Install haystack:
```console
pip install farm-haystack[colab,inference]
```

Install elasticsearch on WSL2 with Ubuntu:
```console
sudo apt-get install openjdk-11-jdk
echo 'export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"'  >> ~/.bashrc
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.9.2-linux-x86_64.tar.gz -q
tar -xzf elasticsearch-7.9.2-linux-x86_64.tar.gz
cd elasticsearch-oss-7.5.2
echo 'export ES_HOME="$HOME/elasticsearch-7.9.2/"' >> ~/.bashrc
echo 'export PATH="$ES_HOME/bin:$PATH"' >> ~/.bashrc
exec $SHELL
elasticsearch --quiet
```
