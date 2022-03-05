#!/bin/bash
cd ../
rm NodeAgent.tar.gz
tar zcvf NodeAgent.tar.gz NodeAgent/*.py NodeAgent/start.sh NodeAgent/prepare.sh
