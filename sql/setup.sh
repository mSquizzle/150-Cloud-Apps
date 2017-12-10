#!/bin/sh

parent=$(dirname $0)
mysql -u root -p --host 127.0.0.1 < $parent/mrs.sql
