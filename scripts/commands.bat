@echo off
REM ============================================================
REM Enemy Soldiers CRUD - OpenShift Commands (READ-ONLY REFERENCE)
REM This file is NOT executable. It only lists the commands to run
REM manually. Copy/paste relevant lines into your terminal.
REM ============================================================

REM ========== Prerequisites ==========
REM - Docker installed, and logged in to Docker Hub
REM - oc CLI installed, and logged in to your OpenShift cluster
REM - Replace placeholders (YOUR_TOKEN, YOUR_API, YOUR_USER, PROJECT) as needed

REM ========== Variables ==========
REM set DOCKER_USER=motiwolff
REM set IMAGE_NAME=enemy-soldiers-api
REM set TAG=v1-amd64
REM set IMAGE=docker.io/%DOCKER_USER%/%IMAGE_NAME%:%TAG%
REM set PROJECT=motiwolff-dev
REM set MONGODB_URI=mongodb://admin:adminpass@mongodb:27017/enemy_soldiers?authSource=admin

REM ========== Login ==========
REM docker login
REM oc login --token=YOUR_TOKEN --server=YOUR_API

REM ========== Select/OpenShift Project ==========
REM oc project %PROJECT%  || oc new-project %PROJECT%

REM ========== Build & Push amd64 Image ==========
REM docker buildx create --use 2>NUL || true
REM docker buildx build --platform linux/amd64 -t %IMAGE% --push .

REM ========== MongoDB (Ephemeral) ==========
REM oc new-app --name=mongodb docker.io/library/mongo:7.0 ^
REM   -e MONGO_INITDB_ROOT_USERNAME=admin ^
REM   -e MONGO_INITDB_ROOT_PASSWORD=adminpass ^
REM   -e MONGO_INITDB_DATABASE=enemy_soldiers
REM oc expose deploy mongodb --port=27017 --target-port=27017 --name=mongodb
REM oc rollout status -w deploy/mongodb

REM ========== (Optional) MongoDB with PVC ==========
REM oc create pvc mongodb-pvc --access-mode=ReadWriteOnce --storage=1Gi
REM oc set volume deployment/mongodb --remove --name=mongodb-volume-1 --confirm
REM oc set volume deployment/mongodb --add --name=mongodb-data --type=pvc --claim-name=mongodb-pvc --mount-path=/data/db
REM oc rollout status -w deploy/mongodb

REM ========== Seed Sample Data (optional) ==========
REM SET MONGOPOD=$(oc get pod -l deployment=mongodb -o jsonpath='{.items[0].metadata.name}')
REM oc exec "%MONGOPOD%" -- mongosh -u admin -p adminpass --authenticationDatabase admin --eval "
REM db = db.getSiblingDB('enemy_soldiers');
REM db.soldier_details.createIndex({id:1},{unique:true});
REM db.soldier_details.insertMany([
REM   {id:1, first_name:'Noa', last_name:'Levi', phone_number:'+972-50-0000001', rank:'Private'},
REM   {id:2, first_name:'Amit', last_name:'Cohen', phone_number:'+972-50-0000002', rank:'Sergeant'}
REM ]);
REM "

REM ========== Deploy FastAPI from Docker Hub ==========
REM oc new-app %IMAGE% --name=enemy-soldiers-api -e MONGODB_URI="%MONGODB_URI%"
REM oc expose deploy enemy-soldiers-api --port=8000 --target-port=8000 --name=enemy-soldiers-api
REM oc expose svc enemy-soldiers-api
REM oc rollout status -w deploy/enemy-soldiers-api

REM ========== Force Always Pull (optional) ==========
REM oc patch deploy enemy-soldiers-api --type=merge -p "{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"enemy-soldiers-api\",\"image\":\"%IMAGE%\",\"imagePullPolicy\":\"Always\"}]}}}}"

REM ========== Get Route & Test ==========
REM set ROUTE=
REM for /f "usebackq tokens=*" %%i in (`oc get route enemy-soldiers-api -o jsonpath="{.spec.host}"`) do set ROUTE=%%i
REM echo http://%ROUTE%
REM curl -vi "http://%ROUTE%/soldiersdb/"
REM curl -vi -X POST "http://%ROUTE%/soldiersdb/" -H "Content-Type: application/json" ^
REM   -d "{\"first_name\":\"Tal\",\"last_name\":\"Shapiro\",\"phone_number\":\"+972-50-0000005\",\"rank\":\"Private\"}"
REM curl -vi "http://%ROUTE%/soldiersdb/1"
REM curl -vi -X PUT "http://%ROUTE%/soldiersdb/1" -H "Content-Type: application/json" -d "{\"rank\":\"Lieutenant\"}"
REM curl -vi -X DELETE "http://%ROUTE%/soldiersdb/1"

REM ========== Logs ==========
REM oc logs -f deploy/enemy-soldiers-api
REM oc logs -f deploy/mongodb

REM ========== Cleanup ==========
REM oc delete route/svc/deploy enemy-soldiers-api --ignore-not-found
REM oc delete route/svc/deploy mongodb --ignore-not-found
REM oc delete pvc mongodb-pvc --ignore-not-found

REM ================== END ==================
REM This .bat is a reference only. Copy the commands you need.
