#!/bin/sh
ack '\((\d{10}\.\d{6})\) can0 (\w{3})\#(\w{2})(\w{2})+' $1 -o > .tmp.fix.log
\mv .tmp.fix.log $2
