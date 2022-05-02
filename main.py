import datetime
import gitlab
import logging as log

log.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level='DEBUG')
log.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))

gl = gitlab.Gitlab('https://gitlab.minikube.gitlab', private_token='fWfvte4DH1W3ZiVuVhL5', ssl_verify=False)


def analyze_pipeline_jobs(pipeline):
    jobs = pipeline.jobs.list()
    for job in jobs:
        artifacts = job.artifacts
        if len(artifacts) > 0:
            # todo search artifacts for 'file_type' === 'trace'. dont download trace if 'size' (in bytes) > avail mem
            trace = gl.http_get(f"/projects/3/jobs/{job.id}/trace")
            sections = list(filter(lambda l: 'section_' in l, trace.text.splitlines()))
            traces_by_label = {}
            complete_traces_list = []
            for section in sections:
                new_section = section[section.index('section_'):]
                section_parts = new_section.split(':')
                if len(section_parts) != 3:
                    log.warning('unexpected format')
                else:
                    start_end = section_parts[0]
                    timestamp = section_parts[1]
                    label = section_parts[2]
                    is_start = 'start' in start_end
                    if label not in traces_by_label:
                        traces_by_label[label] = {}
                    complete_trace = traces_by_label[label]
                    complete_trace['start' if is_start else 'end'] = timestamp
                    complete_trace['label'] = label
                    if 'start' in complete_trace and 'end' in complete_trace:
                        complete_trace['duration'] = int(complete_trace['end']) - int(
                            complete_trace['start'])
                        complete_traces_list.append(complete_trace)
                        del traces_by_label[label]
            log.debug(f'analyzed trace count {len(complete_traces_list)}')
        else:
            log.warning(f'No artifacts found for pipeline={pipeline.id} job={job.id}')
    log.debug(jobs)
    bridges = pipeline.bridges.list()
    for related in bridges:
        child_pipeline_attr = related.downstream_pipeline
        # todo dont do the extra get if we already have the project obj
        child_pipeline = gl.projects.get(child_pipeline_attr['project_id']).pipelines.get(child_pipeline_attr['id'])
        analyze_pipeline_jobs(child_pipeline)


project_3 = gl.projects.get(3)
pipelines = project_3.pipelines.list()
log.info(f'analyzing pipeline count={len(pipelines)}')
for pipeline in pipelines:
    analyze_pipeline_jobs(pipeline)
