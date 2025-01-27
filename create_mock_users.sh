#!/bin/bash

# Function to create a user
create_user() {
  curl --location 'https://localhost:4200/api/user/register' \
  --header 'Content-Type: application/json' \
  --data-raw "$1" \
  --insecure
}

# Create users
create_user '{
  "username": "testusr1",
  "password": "testusr1pass",
  "email": "test1@test.com"
}' &&

create_user '{
  "username": "testusr2",
  "password": "testusr2pass",
  "email": "test2@test.com"
}' &&

create_user '{
  "username": "testusr3",
  "password": "testusr3pass",
  "email": "test3@test.com"
}' &&

create_user '{
  "username": "testusr4",
  "password": "testusr4pass",
  "email": "test4@test.com"
}' &&

create_user '{
  "username": "testusr5",
  "password": "testusr5pass",
  "email": "test5@test.com"
}' &&

create_user '{
  "username": "testusr6",
  "password": "testusr6pass",
  "email": "test6@test.com"
}' &&

create_user '{
  "username": "testusr7",
  "password": "testusr7pass",
  "email": "test7@test.com"
}' &&

create_user '{
  "username": "testusr8",
  "password": "testusr8pass",
  "email": "test8@test.com"
}' &&

create_user '{
  "username": "testusr9",
  "password": "testusr9pass",
  "email": "test9@test.com"
}' &&

create_user '{
  "username": "testusr10",
  "password": "testusr10pass",
  "email": "test10@test.com"
}' &&

create_user '{
  "username": "testusr11",
  "password": "testusr11pass",
  "email": "test11@test.com"
}' &&

create_user '{
  "username": "testusr12",
  "password": "testusr12pass",
  "email": "test12@test.com"
}' &&

create_user '{
  "username": "testusr13",
  "password": "testusr13pass",
  "email": "test13@test.com"
}' &&

create_user '{
  "username": "testusr14",
  "password": "testusr14pass",
  "email": "test14@test.com"
}' &&

create_user '{
  "username": "testusr15",
  "password": "testusr15pass",
  "email": "test15@test.com"
}' &&

create_user '{
  "username": "testusr16",
  "password": "testusr16pass",
  "email": "test16@test.com"
}' &&

create_user '{
  "username": "testusr17",
  "password": "testusr17pass",
  "email": "test17@test.com"
}' &&

create_user '{
  "username": "testusr18",
  "password": "testusr18pass",
  "email": "test18@test.com"
}' &&

create_user '{
  "username": "testusr19",
  "password": "testusr19pass",
  "email": "test19@test.com"
}' &&

create_user '{
  "username": "testusr20",
  "password": "testusr20pass",
  "email": "test20@test.com"
}' &&

create_user '{
  "username": "testusr21",
  "password": "testusr21pass",
  "email": "test21@test.com"
}' &&

create_user '{
  "username": "testusr22",
  "password": "testusr22pass",
  "email": "test22@test.com"
}' &&

create_user '{
  "username": "testusr23",
  "password": "testusr23pass",
  "email": "test23@test.com"
}' &&

create_user '{
  "username": "testusr24",
  "password": "testusr24pass",
  "email": "test24@test.com"
}' &&

create_user '{
  "username": "testusr25",
  "password": "testusr25pass",
  "email": "test25@test.com"
}'