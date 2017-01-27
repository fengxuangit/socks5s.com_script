#!/bin/bash

mysql -u root -p123480 -e "delete from shadow.s_user;"
mysql -u root -p123480 -e "delete from shadow.s_records;"
mysql -u root -p123480 -e "delete from shadow.s_recharge;"
