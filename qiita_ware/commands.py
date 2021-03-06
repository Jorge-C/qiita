# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from os.path import join, isdir
from os import makedirs
from functools import partial

from qiita_db.study import Study
from qiita_ware.ebi import EBISubmission


ebi_actions = ['ADD', 'VALIDATE', 'MODIFY']


def submit_EBI_from_files(study_id, sample_template, prep_template,
                          fastq_dir_fp, output_dir_fp, investigation_type,
                          action, send):
    """EBI submission from files

    Parameters
    ----------
    study_id : int
        The study id
    sample_template : File
        The file handler of the sample template file
    prep_template : File
        The file handler of the prep template file
    fastq_dir_fp : str
        The fastq filepath
    output_dir_fp : str
        The output directory
    investigation_type : str
        The investigation type string
    action : str
        The action to perform with this data, valid options are: %s
    send : bool
        True to actually send the files
    """

    study = Study(study_id)
    study_id_str = str(study_id)

    # Get study-specific output directory and set filepaths
    get_output_fp = partial(join, output_dir_fp)
    study_fp = get_output_fp('study.xml')
    sample_fp = get_output_fp('sample.xml')
    experiment_fp = get_output_fp('experiment.xml')
    run_fp = get_output_fp('run.xml')
    submission_fp = get_output_fp('submission.xml')

    if not isdir(output_dir_fp):
        makedirs(output_dir_fp)
    else:
        raise ValueError('The output folder already exists: %s' %
                         output_dir_fp)

    submission = EBISubmission.from_templates_and_per_sample_fastqs(
        study_id_str, study.title, study.info['study_abstract'],
        investigation_type, sample_template, prep_template,
        fastq_dir_fp)

    submission.write_all_xml_files(study_fp, sample_fp, experiment_fp, run_fp,
                                   submission_fp, action)

    if send:
        submission.send_sequences()
        submission.send_xml()

submit_EBI_from_files.__doc__ %= ebi_actions
