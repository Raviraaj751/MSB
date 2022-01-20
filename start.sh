#iFilmsBotz

if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/ifilmsbotz/MSB.git /MSB
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /MSB
fi
cd /MSB
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
