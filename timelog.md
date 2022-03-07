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

## Week 22

### 03 Mar 2022
* *2.0 hours* Finish Implementation section.
* *1.5 hours* Write up progress around evaluation and main strategy to be performed. High-level Evaluation plan.
* *0.5 hour* Plan out weekly supervisor meeting. 
* *0.5 hour* Carry out weekly supervisor meeting.

## Week 21

### 02 Mar 2022
* *2.5 hours* Progress Deployment subsection of the Implementation section.

### 01 Mar 2022
* *4.0 hours* Carry out more remote experiments as part of the evaluation. Perform scenario analysis and write up conclusions.

### 28 Feb 2022
* *3.0 hours* Create an ML inference benchmark and add it to the suite.
* *1.0 hours* Specify documentation, experiment motivations, and approach.
* *3.0 hours* Carry out remote experiments, implementing small improvements as needed. Save outputs & code.

### 25 Feb 2022
* *1.5 hour* Finish the Benchmarks subsection of Implementation.
* *3.5 hour* Finish the Orchestration subsection of Implementation.

### 24 Feb 2022
* *3.0 hours* Come up with a strategy/approach for Evaluation. Experiments, etc. Write up in summary.
* *1.0 hour* High level Implementation plan.
* *0.5 hour* Plan out weekly supervisor meeting. 
* *0.5 hour* Carry out weekly supervisor meeting.
* *3.5 hours* Progress Implementation chapter as per the plan written above.

## Week 20

### 21 Feb 2022
* *1.5 hour* Write up the monitoring submodule of architecture.
* *1.5 hour* Write up the orchestration submodule of architecture.

### 17 Feb 2022
* *2.0 hours* Review latest feedback and write out architecture section.
* *1.0 hour* Rectify benchmarks subjsection from the modules.
* *1.0 hour* Write out Workloads subsection from the modules.
* *1.0 hour* Prepare and sit regular supervisor meeting.


## Week 19

### 10 Feb 2022
* *1.0 hours* Fix the dissertation introduction as per Yehia's feedback in Jan.
* *1.0 hours* Outline the requirements section, then decide to make it a one-page chapter on its own.
* *1.0 hours* Go on with the Design section - modify current modules paragraphs to reflect requirements.
* *1.0 hours* Start thinking of the architecture section. Create a diagram for high-level operation.
* *0.5 hour* Gather progress, questions, way forward and prepare an agenda for the supervisor meeting.
* *0.5 hour* Sit regular supervisor meeting - lots of feedback on the dissertation. Good!
* *1.0 hour* Edit the diagram as per the feedback on it from the meeting. Start planning the architecture section.


### 08 Feb 2022
* *1.0 hours* Add deployment of other workloads - surprisingly easy. This is good! 
* *1.0 hours* Find, pinpoint, and fix a bug with environment variables - they were getting blended for all workloads and overwritten as subsequent deployments were happening.
* *1.5 hour* Attempt to make building and pushing of images concurrent - took a while and gave up due to time constraints. Added deployment files and tested deployments for all current workloads. Notes
  * The `alexnet` workload spanws and runs normally but gets killed. Probably due to performance limits.
  * The `text-analysis` workload runs too quicky and finishes before Prometheus has detected it.


## Week 18

### 04 Feb 2022
* *2.0 hours* Implement log fetching for each workload, add hierarchy to the logs folder for deployment to add runtime logs of workloads.
* *2.0 hours* Improve error handling to:
  * Support manual stop of experiments. 
  * Collect logs even though crashes occur.
* *2.0 hours* Figure out the coordination of prometheus and workloads as they are being deployed. Attempt multiple variants and evaluate impacts on experiments. In the case of DNS access of workloads, we achieve simplicity with about 2-3 minute maximum loss of monitoring over experiment time.

### 03 Feb 2022
* *2.0 hours* Went on implementing deployment via Python SDK. Bumped onto an issue with the docker-compose context - contradicts the design of orchestration.
* *3.0 hours* Went forward with the `docker compose` context and the ACI - Docker implementation.
  * Changed docker-compose images to use configuration for deploying the ACIs
  * Added envvar exporting and support for the images so configuration is unified in the `experiment.yml`
  * Created support for different filename of the compose file. So the local context one is conventional.
* *0.5 hour* Gather progress and meeting notes and plan out supervisor meeting.
* *0.5 hour* Sit supervisor meeting and upload the notes.
* *1.0 hour* Implement gathering of Prometheus metrics for deployment.
* *1.0 hour* Implement finish file polling for deployment.
* *1.0 hour* Finish end-to-end experiment deployment through the `docker compose` context. Err handling & Logs left.

## Week 17

### 27 Jan 2022
* *2.5 hours* Attempt to make building and pushing of images concurrent in deployment. Realise it is low priority, put in a task (#6) and go on.
* *2.5 hours* Going on with deployment of multi-container instance groups. Blocker of wrongly implemented examples in Azure documentation stopped me for a while.
* *0.5 hour* Prepare meeting agenda - notes, questions, progress.
* *0.5 hour* Sit regular weekly supervisor meeting.
* *2.0 hours* Resolve bug/uncertainty around Azure documentation and made multi-instance containers groups be successfully deployed now.
* *2.0 hours* Force restarts when needed on deployment. Figure out several issues:
  * Compose files/config is not parsed when individual images are built/pushed through their corresponding dockerfiles.
  * Azure instances within a given container instance group share a host - this hurts representativeness. However, resources are allocated to individual instances and can be limited. 
  * Logs will be hard to be implemented.

### 25 Jan 2022
* *2.0 hours* Implement a shared Azure volume for management of finish files. 
* *1.0 hour* Scaffold multi-container image pushing and deployment.

## Week 16

### 20 Jan 2022
* *3.0 hours* Dockerize and deploy orchestrator instance. Automate login, image pushes, and deployment.
* *Due to a GitHub/VSCode mistake, lost last 5 hours of code progress*
* *0.5 hour* Plan for the meeting - progress, questions, agenda, etc.
* *0.5 hour* Sit regular supervisor meeting.
* *3.0 hour* Make up on progress on automating HelioBench Azure deployment. Realise there is no need for an individual orchestrator instance - all can be done by the host.
* *3.0 hours* Implement Prometheus image pushing and deployment. 
* *1.0 hour* Add linting and virtual environment to the project for ease of use.

### 17 Jan 2022
* *1.0 hour* Start implementing the designed architecture. 
* *1.0 hour* Manually experiment with containers and deployments.

## Week 15

### 15 Jan 2022
* *2.0 hours* Research Azure services which would facilitate deployment.
* *1.0 hour* Start planning an architecture for deployment via Azure Container Instances.

### 14 Jan 2022
* *1.5 hour* Expand last argument from the Benchmark section. Include experiment + graphs.
* *1.5 hour* Finish expanding penultimate argument from the Benchmark section. Include tables and rationale.

### 13 Jan 2022
* *0.5 hour* Update hours for the last several days.
* *0.5 hour* Update kickoff meeting progress and agenda.
* *0.5 hour* Have semester 2 kickoff meeting and record notes.

### 11 Jan 2022
* *1.5 hour* Go on expanding parts of the design section of the dissertation. 
* *0.5 hour* Gather all questions I have and forward to Yehia in advance of the kickoff meeting.

### 10 Jan 2022
* *1.0 hour* Finalise introduction (motivation + main idea + contributions).
* *1.5 hour* Plan out the rest of the design section and start expaning modules (easiest as I know what to write).

## Week 14

### 07 Jan 2022
* *2.5 hours* Plan out better and write some of the dissertation introduction.
* *1.0 hour* Look through all project documentation and start planning out the design section.

### 03 Jan 2022
* *0.5 hour* Get back to context after a long break and plan out the implementation of a unified Prometheus architecture.
* *2.0 hours* Plan and implement a new configuration system. Includes environment variables injected into each service on startup, and a general ```environment``` section for global experiment options.
* *3.0 hours* Implement a single Prometheus, linking to all benchmarks, available for logging. Includes all orchestrator functions.
* *2.0 hours* Integrate the latest orchestrator into all services and ensure they all work correctly.

## Week 11

### 17 Dec 2021
* *2.0 hours* Start integrating the ```nginx-web``` benchmark. Bump upon Prometheus server issue (see [1](https://github.com/FrogBattle/HelioBench/issues/1)).
* *1.0 hour* Create a config module for parsing an experiment configuration file.
* *0.5 hour* Plan out and sit supervisor meeting.
* *2.0 hours* Complete and submit status report.
* *1.0 hour* Ensure the version with many Prometheus servers and a config file works for the three benchmarks in parallel.

### 16 Dec 2021
* *1.0 hour* Research how to work with volumes via auxiliary scripts in Docker-managed volumes. 
* *1.0 hour* Create modules for working with such volumes and test it succeeds.
* *3.0 hours* Plan and implement general orchestrator - subprocess for each benchmark.
* *1.0 hour* Create the log- and metric-collection modules.
* *1.0 hour* Integrate ```memcached``` as well as ```go-api``` and run them simultaneously.

## Week 10

### 09 Dec 2021
* *0.5 hour* Engage with more resources about how to write.
* *1.0 hour* Expand some sections with high-level plan, put in questions, and action items for the dissertation. Send an email to Yehia, asking for feedback.
* *1.0 hour* Research into starting and stopping (depending) containers consistently. Wait-for vs Dockerize. Leave for now.
* *1.0 hour* Look into a native way to work with the TSDB from Promscale. Way too difficult. Allows for persistance & scaling, but not for our needs.
* *1.0 hour* Create a recursive script to pull all data at the end of a given experiment. 

### 08 Dec 2021
* *0.5 hour* Download project template and transfer to Overleaf.
* *1.0 hour* Start reading/watching on how to write - see sources in guides.
* *0.5 hour* Start putting in preliminary sections. Finish tomorrow and give Yehia for review.

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