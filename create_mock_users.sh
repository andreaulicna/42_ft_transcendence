#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Provide one parameter, specifying the number of users you want to create"
	exit 1
fi

ITER_VAR=1
create_user() {
  curl --location 'https://localhost:4200/api/user/register' \
  --header 'Content-Type: application/json' \
  --data-raw "{
  \"username\": \"testusr${ITER_VAR}\",
  \"password\": \"testusr${ITER_VAR}pass\",
  \"email\": \"test${ITER_VAR}@test.com\"
	}" \
  --insecure
}

while [ $ITER_VAR -le  $1 ];
do
	create_user
	echo
	ITER_VAR=$((ITER_VAR + 1))
done