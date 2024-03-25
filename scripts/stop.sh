# if .pid exists, kill the process, else echo "No process running"
if [ -f .pid ]; then
  kill `cat .pid`
  rm .pid
else
  echo "No process running"
fi
