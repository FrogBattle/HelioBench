# Timelog

* Microservices Benchmarking Suite
* Alexander Simeonov
* 2390362S
* Yehia Elkhatib

## Guidance

* This file contains the time log for your project. It will be submitted along with your final dissertation.
* **YOU MUST KEEP THIS UP TO DATE AND UNDER VERSION CONTROL.**
* This timelog should be filled out honestly, regularly (daily) and accurately. It is for *your* benefit.
* Follow the structure provided, grouping time by weeks.  Quantise time to the half hour.

## Week 9

### 03 Dec 2021
* *2.0 hours* Research ways Prometheus stores data. Consume web API vs TSDB connector.
* *1.0 hour* Research basic raw metrics Prometheus scrapers give - CPU, MEM, IO.
* *1.0 hours* Create an example web API consumption script which consumes Prometheus' API.
* *0.5 hour* Prepare meeting agenda and bump timelogs.
* *0.5 hour* Put in initial dissertation structure in Overleaf.
* *0.5 hour* Have the regular supervisor meeting.

## Week 8

### 24 Nov 2021
* *1.5 hour* Research MS application using Go services. Sock shop, Robot shop, Digota. High coupling and complexity.
* *0.5 hour* Find a small example Go API and dockerize it.
* *1.0 hour* Find an example locust runner, dockerize it, customise it to work with our app.
* *0.5 hour* Implement prometheus and put the whole benchmark together.

## Week 7

### 18 Nov 2021
* *1 hour* Start looking into Memcached and get the workload runner working.
* *0.5 hour* Review last meeting notes and create a meeting agenda.
* *0.5 hour* Have a supervisor meeting, upload relevant outcomes.

### 17 Nov 2021
* *2 hours* Try to get on board with the PetClinic Spring API benchmark. Config service issues. Discovery service issues.
* *1 hour* Try to get "microService" Spring API benchmark. Discovery service issues - server simply not starting. Built on top of SockShop images (Weaveworks).
* *0.5 hour* Got small ML benchmark application. Runs too quickly and there are no larger datasets available. Representitiveness is questionable.

### 11 Nov 2021
* *1 hour* Review the requirements, high-level project plan, previous meeting minutes, include questions, progress and agenda for the meeting.
* *1 hour* Try to decouple the PetClinic Spring MS from the whole application, surface problems, include in meeting agenda.
* *0.5 hour* Have meeting with Yehia, gather meeting minutes and send to relevant repos.

### 10 Nov 2021
* *1.0 hour* Poke around the Sock Shop Spring MSs to figure out a way to include a Spring API benchmark. Establish very high coupling between services and no way to mock inditividual Spring API service.
* *1.0 hour* Look at the PetClinic MS app. The `/vets` endpoint seems quite standalone with all (generic) dependencies. Eg: service discovery, config server, vets service, prometheus. Some can be reduced to isolate better.

### 08 Nov 2021
* *0.5 hour* Send an email to Yehia about MoSCoW user stories (requirements) in Trello.
* *1.5 hour* Get an nginx web application in store. Also create a workload service for it.
* *2.0 hours* Create a Prometheus service to run on the benchmark. Create a docker compose for all services

## Week 6

### 04 Nov 2021
* *1.5 hour* Struggled with running MLPerf's recommender benchmark - no success. Realised it is too complex. Changed direction.
* *1.5 hour* Found a tutorial for AlexNet with small dataset using Tensorflow. Dockerised it. Made a shell script to monitor.
* *0.5 hour* Reviewing progress, coming up with meeting points, preparing for the incoming meeting.
* *1.0 hour* Had meeting, reviewed and pushed notes, recorded APs, etc.
* *1.5 hour* Struggling with different MLPerf workloads. Trying to go around Nvidia & Cuda. No success.
* *1.0 hour* Reviewing AIBench's zenodo (repo with data). Realising they do NOT have all the data again (LFS placeholders still there). Sad.

### 03 Nov 2021
* *1.0 hour* Struggled with Fanthom's seq2seq and autoenc benchmarks - no success.
* *1.0 hour* Struggled with MLPerf's recommender benchmark - no success so far. Seems better!

## Week 5

### 29 Oct 2021
* *1.5 hours* Came up with a preliminary list of MSs to get in house. Sent to Yehia.
* *1.5 hour* Attempting to setup a Fathom ML app (seq2seq) as a Docker container.

### 28 Oct 2021
* *2 hours* Finished containerising MicroSuite's dependencies Dockerfile. 
* *0.5 hour* Plan out meeting agenda points and questions.
* *0.5 hour* Have regular supervisor meeting.
* *1.0 hour* Look into taking the seq2seq MS from Fathom inhouse.

### 27 Oct 2021
* *1.5 hour* Started containerising MicroSuite's ML app (HDSearch) in house as a submodule. Problem with enormous image building times ± an hour.
* *1.5 hour* Researched the area of AI-based microservice benchmarks and documented findings.

### 26 Oct 2021
* *0.5 hour* Composed an email to AIBench's creators for GitHub LFS file transfer.
* *0.5 hour* Rename repos + Trello, review notes, and update Methodology for the project on Trello.
* *1 hour* Research into smaller benchmarking applications (workloads).
* *1 hour* Research into AI-based benchmarking applications (workloads).

## Week 4

### 21 Oct 2021
* *2 hour* Debugged a big part of AIBench - established problems with GitHub LFS files. Main blocker!
* *1 hour* Managed to work around some AIBench problems - recompiled libraries, retreieved some LFS files.
* *0.5 hour* Changed Trello objectives to reflect latest understanding of the project.
* *0.5 hour* Come up with a meeting agenda, reflecting progress, updates, questions, etc.
* *0.5 hour* Had meeting, reviewed notes and updated all docs to reflect this.

### 18 Oct 2021
* *1.5 hour* Looked at installing and running the AIBench e-commerce scenario for integrating it into the suite.
* *0.5 hour* Looked at the storyboard better, scheduled a quick adhoc meeting, and added questions for it.
* *0.5 hour* Had an adhoc meeting, recorded notes.
* *2.0 hours* Keep attempting to run all components of AIBench - resolving the issue with unavailable Git LFS files.

## Week 3

### 14 Oct 2021
* *1.0 hour* Prepared better meeting agenda and made dissertation GitHub repo.
* *1.0 hour* Started researching how to implement some AI app on MS architecture (DSB). AlexNet or AIBench app.
* *0.5 hour* Had meeting and recorded notes + minutes

### 12 Oct 2021
* *2.5 hour* Laid out basic project direction (objectives + methodologies) and documented them in Trello.
* *1.5 hour* Started narrowing objectives and researching how to go about achieving them.

## Week 2

### 07 Oct 2021
* *1.5 hour* Skimmed the AIBench publication and took notes.
* *1.5 hour* Read the Pattern based benchmarking publication and took notes.
* *0.5 hour* Created and sent out meeting agenda for later today.
* *0.5 hour* Had a meeting and send out action points.
* *1.5 hour* Setting up and playing with DeathStarBench.

### 05 Oct 2021
* *2 hours* Read the DeathStarBench publication and take notes.

### 04 Oct 2021
* *1 hour* Setup a repo, Trello, JabRef, Docker, and DeathStarBench.

## Week 1

### 29 Sep 2021
* *0.5 hour* Had first supervisor meeting and took notes.

### 28 Sep 2021
* *0.5 hour* Arranged first supervisor meeting and created an agenda.