#!/usr/bin/env python3
"""Original evergreen cloud-AI schematics. CC-BY-4.0, AI Update Sources.

These are explanatory diagrams, never empirical model scores or company art.
"""
from pathlib import Path
import json, re, math, html, hashlib, textwrap, subprocess, concurrent.futures

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
QA = ROOT / 'qa'
ASSETS.mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)

# title | composition | labeled nodes | subtitle | interpretation note
# Every record describes a different technical concept. Layout choice follows
# the relationship being explained rather than a cosmetic asset multiplier.
GROUPS = [
('Cloud request lifecycle', [
('A cloud inference request', 'flow', ['Client request', 'Cloud endpoint', 'Model generation', 'Response', 'Client display'], 'A hosted model returns a response to an application request.', 'Schematic: client and provider responsibilities vary by service.'),
('Streaming and complete responses', 'split', ['Model response', 'Streaming chunks', 'Complete payload', 'Client presentation'], 'Streaming exposes partial output before the full response is available.', 'Streaming changes delivery; it does not establish higher answer quality.'),
('A request with validation', 'gate', ['Request draft', 'Input valid?', 'Send request', 'Reject invalid input', 'Record outcome'], 'Validate required fields before a cloud request is submitted.', 'Input validation does not prove that the generated answer is correct.'),
('A retry after a transient failure', 'cycle', ['Submit request', 'Transient failure', 'Wait with backoff', 'Retry within budget'], 'A bounded retry loop can recover from some temporary failures.', 'Retries may incur cost; avoid repeating external side effects.'),
('Timeout versus model failure', 'compare', ['Client deadline', 'Request may continue', 'Provider error', 'Request may stop'], 'A client timeout and a provider error are different events.', 'Confirm request state before retrying a timed-out operation.'),
('Tracking a request end to end', 'flow', ['Local request ID', 'Provider request ID', 'Usage record', 'Outcome record'], 'Link request identity, usage, and outcome for later review.', 'IDs help trace a request; they are not evidence of correctness.'),
('Conversation across turns', 'cycle', ['User message', 'Model response', 'Selected history', 'Next request'], 'Applications decide which earlier messages to include in later requests.', 'Conversation persistence is platform-specific; inspect the active context.'),
('An API and its surrounding app', 'hub', ['Application', 'Cloud model', 'User interface', 'History storage', 'Usage accounting', 'Output checks'], 'A model endpoint is one part of the complete user experience.', 'Do not attribute every application feature to the underlying model.'),
('Request cancellation', 'split', ['Cancel action', 'Client stops waiting', 'Provider cancellation', 'Check billed usage'], 'Stopping the interface and cancelling cloud execution may differ.', 'Cancellation and billing behavior depend on the provider.'),
('A bounded generation budget', 'stack', ['Task requirements', 'Output limit', 'Reasoning setting', 'Timeout', 'Spending limit'], 'Set explicit bounds around generation and application behavior.', 'Controls and billing categories differ across services.'),
]),
('Prompt and instruction design', [
('The anatomy of a useful prompt', 'stack', ['Task goal', 'Relevant context', 'Constraints', 'Output format', 'Success criteria'], 'A useful prompt states the task and the conditions for a good answer.', 'Keep instructions necessary and test whether each addition helps.'),
('Prompt versus reference material', 'compare', ['Instructions', 'Behavior to follow', 'Reference material', 'Content to examine'], 'Separate instructions from the information the model should inspect.', 'Reference text can contain misleading instructions; treat it as data.'),
('Examples as format guidance', 'flow', ['Desired behavior', 'Representative example', 'New input', 'Generated output'], 'Examples can communicate an expected format or task pattern.', 'Examples should represent the task without leaking test answers.'),
('A structured output contract', 'gate', ['Generated response', 'Schema valid?', 'Accept structured record', 'Reject invalid record', 'Validation record'], 'Validate the response against the required structure before use.', 'A valid schema does not guarantee truthful or useful content.'),
('Resolving ambiguous requests', 'split', ['Ambiguous request', 'Ask for key context', 'State safe assumption', 'Proceed with clarity'], 'Missing information can require a question or a stated assumption.', 'Choose based on how much the missing context changes the result.'),
('A reusable task template', 'merge', ['Stable instructions', 'Variable task data', 'Filled prompt', 'Cloud request'], 'Separate reusable instructions from values that change each run.', 'Version templates so comparisons remain reproducible.'),
('Conflicting instructions', 'gate', ['Instruction set', 'Conflict present?', 'Clarify priority', 'Retain clear instructions', 'Coherent task'], 'Conflicting requirements make intended behavior harder to evaluate.', 'Instruction handling differs by platform; test the actual system.'),
('Prompt scope and effort', 'triangle', ['Required task', 'Relevant detail', 'Evaluation criteria'], 'Align instructions with the task rather than adding unrelated detail.', 'Longer prompts are not automatically better prompts.'),
('Iterating a prompt using evidence', 'cycle', ['Prompt version', 'Representative test', 'Observed failure', 'Targeted revision'], 'Change prompts to address observed failures on representative tasks.', 'Avoid tuning only to the examples used for development.'),
('Task data inside a boundary', 'stack', ['Task instructions', 'Delimited data', 'Requested transformation', 'Output constraints'], 'Clear boundaries help distinguish source content from instructions.', 'Delimiters alone are not a security guarantee.'),
]),
('Context and tokens', [
('What enters the context', 'merge3', ['Instructions', 'Conversation history', 'Reference excerpts', 'Active context'], 'A request can combine several kinds of input within its context.', 'The exact components depend on the app and endpoint.'),
('Characters are not tokens', 'compare', ['Readable text', 'Characters and words', 'Tokenizer output', 'Model-specific tokens'], 'Token counts depend on the tokenizer and the input content.', 'Never assume a fixed character-to-token ratio for billing.'),
('Input and generated tokens', 'split', ['Model request', 'Input tokens', 'Generated tokens', 'Usage accounting'], 'Input and output token categories describe different parts of a request.', 'Some services report additional billed token categories.'),
('Context capacity and useful recall', 'compare', ['Context capacity', 'How much can fit', 'Useful recall', 'What is correctly used'], 'A large context allowance does not establish reliable recall.', 'Test retrieval and synthesis on documents resembling the real task.'),
('History selection', 'funnel', ['Full conversation', 'Relevant turns', 'Selected context', 'Next response'], 'Select history that supports the current task.', 'Removing history can lose constraints; verify the resulting behavior.'),
('Summarizing earlier turns', 'flow', ['Earlier messages', 'Summary', 'Current request', 'Model response'], 'A summary can reduce history size while carrying forward key details.', 'Summaries can omit or distort information and should be checked.'),
('Finding detail in long documents', 'tree', ['Document task', 'Evidence location', 'Evidence meaning', 'Verify page and passage', 'Compose supported answer'], 'Document length and evidence location can affect practical performance.', 'Use task-specific tests instead of context size alone.'),
('Output length consumes a budget', 'stack', ['Task needs', 'Requested detail', 'Output allowance', 'Possible truncation'], 'A generation limit can stop a response before the task is complete.', 'Inspect truncation and finish reasons where available.'),
('Cached and fresh input', 'compare', ['Reusable input', 'Potential cache hit', 'Changed input', 'Fresh processing'], 'A provider cache may treat repeated and new input differently.', 'Cache eligibility, rates, and duration vary by service.'),
('Conversation state and user memory', 'compare', ['Current context', 'Request-visible text', 'Platform memory', 'Saved preferences or facts'], 'Conversation context and persistent memory are different mechanisms.', 'Platform memory behavior must be verified for the service used.'),
]),
('Output and answer control', [
('Formatting versus truth', 'compare', ['Correct format', 'Structure matches', 'Correct content', 'Claims are supported'], 'A response can satisfy formatting requirements while being wrong.', 'Evaluate structure and substance separately.'),
('Answer length and completeness', 'triangle', ['Necessary detail', 'Clear organization', 'Complete task'], 'Concise answers should still satisfy the full task.', 'Shorter output is useful only when essential content remains.'),
('A factual answer with evidence', 'flow', ['Question', 'Relevant evidence', 'Answer claims', 'Citation check'], 'Check that cited evidence supports the claims made in the answer.', 'A plausible-looking citation is not proof of source support.'),
('When a model should express uncertainty', 'gate', ['Question', 'Evidence sufficient?', 'Qualified answer', 'State uncertainty', 'Useful next step'], 'An answer should communicate meaningful uncertainty about its support.', 'Uncertainty wording is not a calibrated probability estimate.'),
('Separating observation from inference', 'compare', ['Observed evidence', 'Directly supported', 'Interpretation', 'Reasoned inference'], 'Distinguish what sources state from the conclusion drawn from them.', 'Label inferences and explain the assumptions that matter.'),
('A draft followed by checks', 'flow', ['Initial draft', 'Requirement check', 'Evidence check', 'Revised output'], 'Review both task compliance and factual support before delivery.', 'An additional model review can share the original model’s errors.'),
('Response status categories', 'matrix', ['Successful result', 'Partial result', 'Refusal', 'Error', 'Truncated output', 'Unsupported answer'], 'Record outcomes more precisely than simply success or failure.', 'Define outcome categories before scoring comparisons.'),
('A machine-readable answer', 'flow', ['User task', 'Schema-guided response', 'Parser', 'Application action'], 'Structured responses can connect model output to application logic.', 'Validate values and permissions before acting on the output.'),
('Extracting versus inventing', 'compare', ['Extraction task', 'Use supplied evidence', 'Generation task', 'Create new material'], 'Extraction should preserve source facts rather than fill unknown gaps.', 'Label missing fields instead of making them appear documented.'),
('A recommendation with a boundary', 'stack', ['Recommended option', 'Task fit', 'Cost basis', 'Known limitation', 'When to reconsider'], 'A useful recommendation explains both its reason and its limits.', 'Date recommendations because model and platform behavior can change.'),
]),
('Tools and external actions', [
('A tool call lifecycle', 'flow', ['User request', 'Model proposes call', 'App validates call', 'Tool executes', 'Result returns'], 'Applications mediate model-proposed calls to external tools.', 'A proposed tool call is not evidence that the tool ran.'),
('Tool result returns to the model', 'cycle', ['Model request', 'Tool execution', 'Tool result', 'Model follow-up'], 'Tool outputs can inform a later response or another tool request.', 'The app should bound repeated tool use and record failures.'),
('Tool selection and argument validity', 'compare', ['Select correct tool', 'Task matches capability', 'Valid arguments', 'Inputs match requirements'], 'A correct tool name does not establish a valid invocation.', 'Evaluate selection, argument correctness, execution, and outcome.'),
('Read-only and state-changing tools', 'split', ['Requested action', 'Read-only operation', 'State-changing operation', 'Permissions before execution'], 'Reading information and changing external state carry different consequences.', 'Apply the permissions and confirmation rules of the actual app.'),
('Permissions around a tool', 'gate', ['Proposed action', 'Authorized scope?', 'Execute within scope', 'Request clarification', 'Record outcome'], 'Check authority before an external operation is executed.', 'Natural-language permission and app credentials are distinct.'),
('Handling a tool error', 'gate', ['Tool response', 'Usable result?', 'Use returned evidence', 'Handle failure', 'Honest answer'], 'Tool failures should not be silently replaced by invented results.', 'Report limitations or choose a permitted alternative.'),
('Independent tool tasks', 'split', ['Work request', 'Independent lookup A', 'Independent lookup B', 'Combine results'], 'Independent operations may be run concurrently.', 'Concurrency is appropriate only when tasks do not depend on each other.'),
('Dependent tool tasks', 'flow', ['Find record', 'Read selected record', 'Prepare update', 'Submit authorized update'], 'A later operation may require the result of an earlier one.', 'Preserve ordering when correctness depends on prior results.'),
('A bounded agent loop', 'cycle', ['Plan next action', 'Execute permitted tool', 'Check progress', 'Continue or stop'], 'An agent loop should have clear success and stopping conditions.', 'Bound time, cost, and actions; do not equate activity with progress.'),
('Responsibility for external actions', 'hub', ['Application controls', 'Tool allowlist', 'Argument validation', 'User authority', 'Execution logging', 'Failure handling'], 'The surrounding application must govern external tool behavior.', 'A model prompt alone does not replace application controls.'),
]),
('Search and research', [
('Search is not source verification', 'flow', ['Search results', 'Open original source', 'Read relevant passage', 'Verify claim'], 'Search locates potential evidence; the source must support the claim.', 'Snippets may omit qualifications or refer to older information.'),
('A research answer pipeline', 'flow', ['Research question', 'Find sources', 'Compare evidence', 'Synthesize answer', 'Attach citations'], 'A sourced answer connects evidence to each substantive claim.', 'Citations should support nearby claims directly.'),
('Primary and secondary evidence', 'compare', ['Primary source', 'Original claim or result', 'Secondary source', 'Interpretation or reporting'], 'Different source types answer different verification questions.', 'Official announcements can verify launches without proving superiority.'),
('Claim and citation alignment', 'merge3', ['Answer claim', 'Supporting passage', 'Source identity', 'Verified citation'], 'Verify the passage, source, and claim together.', 'Do not cite a page only because it concerns the same broad topic.'),
('Two sources disagree', 'split', ['Conflicting reports', 'Compare dates', 'Compare definitions', 'Explain disagreement'], 'Differences can arise from timing, scope, or measurement methods.', 'Do not resolve disagreement by selecting the most convenient number.'),
('Research freshness', 'stack', ['Publication date', 'Event date', 'Access date', 'Episode cutoff'], 'Distinguish when something happened from when it was reported.', 'A recent webpage is not automatically evidence of a recent event.'),
('Search settings affect results', 'hub', ['Research context', 'Query wording', 'Language', 'Region', 'Date filtering', 'Access limitations'], 'Record settings that meaningfully influence discovered evidence.', 'Search coverage is incomplete; absence of a result is not proof.'),
('A source for each claim', 'tree', ['Episode conclusion', 'Claim A', 'Claim B', 'Source support A', 'Source support B'], 'Break conclusions into claims that can each be checked.', 'Several repeated reports may share one original source.'),
('Cited sources and unsupported additions', 'gate', ['Draft claim', 'Claim supported?', 'Retain supported claim', 'Remove unsupported claim', 'Revised draft'], 'Check the full answer rather than only its citations section.', 'Source support must match the stated level of certainty.'),
('Research within a time budget', 'funnel', ['Possible leads', 'Relevant sources', 'Verified evidence', 'Decision-ready answer'], 'Focus research on evidence that changes the viewer’s decision.', 'A time budget does not justify inventing missing support.'),
]),
('Files and document tasks', [
('File upload versus model input', 'flow', ['Uploaded file', 'Platform processing', 'Model-visible content', 'Generated answer'], 'An uploaded file may be transformed before the model receives it.', 'Do not assume every page or object reaches the model unchanged.'),
('A scanned document', 'flow', ['Page image', 'Text recognition', 'Extracted text', 'Verification'], 'Image-only documents can require text recognition before analysis.', 'Recognition errors can alter names, numbers, and table structure.'),
('A document question with a citation', 'flow', ['User question', 'Relevant page', 'Supported answer', 'Page reference'], 'Connect document answers to the actual supporting location.', 'Page references should match the delivered file and its numbering.'),
('Tables are more than text', 'matrix', ['Column headers', 'Row labels', 'Values', 'Units', 'Footnotes', 'Cell relationships'], 'Table meaning depends on structure, labels, and qualifications.', 'Verify extracted values together with units and header alignment.'),
('A chart-reading task', 'stack', ['Axes and units', 'Legend', 'Data marks', 'Annotations', 'Supported conclusion'], 'Chart interpretation requires reading the visual encoding.', 'Do not infer precise values from an unreadable chart image.'),
('Extraction from several files', 'merge', ['File A', 'File B', 'Shared extraction schema', 'Combined records'], 'A common schema makes extracted document facts comparable.', 'Preserve file identity for every extracted record.'),
('Cross-document disagreement', 'compare', ['Document A', 'Date and claim', 'Document B', 'Date and claim'], 'Conflicting files require their dates and scopes to be checked.', 'Do not merge incompatible versions into one undocumented fact.'),
('A spreadsheet analysis task', 'flow', ['Workbook data', 'Type and unit checks', 'Analysis', 'Reproducible result'], 'Confirm data interpretation before using calculations in an answer.', 'Model-produced calculations should be checked with deterministic tools.'),
('An exported artifact', 'flow', ['Task requirements', 'Generated file', 'Open and inspect', 'Deliver file'], 'A file is complete only when the intended content is usable.', 'Verify formatting, embedded objects, and application compatibility.'),
('Sensitive data in a cloud file', 'gate', ['File selection', 'Appropriate to upload?', 'Prepare permitted content', 'Keep file out of cloud', 'Record decision'], 'Select and prepare file content according to the task’s permissions.', 'Provider policies and account settings must be checked separately.'),
]),
('Multimodal cloud use', [
('Text and image in one request', 'merge', ['Text instruction', 'Image input', 'Multimodal processing', 'Response'], 'The task can combine written instructions with visual evidence.', 'Verify image support and input limits for the actual endpoint.'),
('What an image task asks for', 'matrix', ['Describe content', 'Read visible text', 'Compare images', 'Interpret chart', 'Locate object', 'Explain diagram'], 'Different visual tasks require different evaluation criteria.', 'General image support does not imply equal skill on every task.'),
('Image detail and readability', 'triangle', ['Source resolution', 'Crop selection', 'Visible evidence'], 'The supplied image must make the relevant details observable.', 'Higher resolution does not repair missing or obscured information.'),
('Image observation and inference', 'compare', ['Visible features', 'Direct observations', 'Interpretation', 'Context-dependent inference'], 'Describe what is visible separately from what it might mean.', 'Avoid confidently assigning hidden causes from an image alone.'),
('Audio input and transcription', 'flow', ['Speech audio', 'Transcription', 'Text interpretation', 'Answer'], 'A speech task may involve separate recognition and reasoning stages.', 'Some multimodal services process audio differently; verify their design.'),
('Transcript and original audio', 'compare', ['Transcript', 'Recognized words', 'Audio', 'Timing and sound cues'], 'Text transcription does not preserve every feature of the audio.', 'Task requirements determine whether the original audio is necessary.'),
('Video as frames and time', 'stack', ['Visual frames', 'Frame timestamps', 'Audio context', 'Temporal task'], 'Video interpretation must connect content to when it occurs.', 'Frame sampling can miss brief actions or changes.'),
('Comparing image outputs', 'matrix', ['Prompt adherence', 'Visible quality', 'Text accuracy', 'Editing fidelity', 'Consistency', 'Task usability'], 'Evaluate generated images according to the intended use.', 'Do not treat aesthetic preference as proof of factual accuracy.'),
('A multimodal evidence chain', 'flow', ['Original media', 'Selected region', 'Observed detail', 'Supported claim'], 'Keep the underlying media linked to the visual claim it supports.', 'Cropping must not remove context that changes the interpretation.'),
('Modalities and platform features', 'hub', ['Cloud experience', 'Text input', 'Image input', 'Audio input', 'File handling', 'Generated media'], 'The platform exposes capabilities around its available models.', 'Feature availability varies by plan, region, and endpoint.'),
]),
('Platform features and user workflows', [
('Model versus platform capability', 'compare', ['Model capability', 'Generates and reasons', 'Platform capability', 'Tools and user workflow'], 'Evaluate the hosted model and the surrounding product separately.', 'A benchmark for a model does not prove every platform feature works.'),
('A project workspace', 'hub', ['Project workspace', 'Instructions', 'Files', 'Conversations', 'Task context', 'Shared references'], 'A workspace can organize inputs that recur across related tasks.', 'Verify which workspace contents are included in each request.'),
('Reusable instructions in a platform', 'flow', ['Saved instructions', 'Current task', 'Active context', 'Response'], 'Saved preferences can influence repeated tasks when applied.', 'Persistent instructions may interact with task-specific constraints.'),
('Memory settings as a user choice', 'gate', ['Memory feature', 'Appropriate for task?', 'Use permitted memory', 'Disable or clear', 'Check behavior'], 'Users should understand what information a memory feature retains.', 'Settings and retention behavior are platform-specific.'),
('Deep research and ordinary chat', 'compare', ['Ordinary chat', 'Immediate interaction', 'Research workflow', 'Search and synthesis'], 'A research workflow may add retrieval and analysis steps around a model.', 'Compare the complete workflow, including time and tools used.'),
('A coding workspace workflow', 'cycle', ['Describe change', 'Inspect files', 'Edit code', 'Run meaningful checks'], 'Useful coding assistance includes verification of the resulting change.', 'A code snippet alone does not establish a complete working feature.'),
('Connector-enabled information access', 'flow', ['User authority', 'Connected service', 'Retrieved record', 'Supported response'], 'A connector can supply account-specific data within authorized scope.', 'Connection access is not authorization for every possible action.'),
('Voice mode as an experience', 'cycle', ['User speaks', 'Recognize input', 'Generate response', 'Speak output'], 'Conversational voice combines several stages of the interaction.', 'Evaluate interruption, recognition, and latency as separate concerns.'),
('Scheduled and immediate tasks', 'compare', ['Immediate request', 'Run now', 'Scheduled task', 'Run at a future trigger'], 'Scheduling changes when a workflow runs rather than proving its quality.', 'Check future-task availability and execution status for the platform.'),
('A feature tutorial that helps users', 'flow', ['User goal', 'Feature location', 'Concrete action', 'Useful output', 'Known limitation'], 'Demonstrate what to do and the result the user can expect.', 'Document the plan, region, interface, and date of the demonstration.'),
]),
('Cost and cloud economics', [
('Total task cost', 'merge3', ['Input charges', 'Generation charges', 'Tool and retry charges', 'Total task cost'], 'Sum the applicable charges for the actual task.', 'Do not assume all providers use the same billing categories.'),
('Unit price versus task cost', 'compare', ['Unit price', 'Rate per billing unit', 'Task cost', 'Usage times applicable rates'], 'A lower token rate does not necessarily mean a lower completed-task cost.', 'Output length, retries, tools, and settings can change usage.'),
('Cost per successful result', 'funnel', ['All attempted requests', 'Total attempt cost', 'Successful outcomes', 'Cost per success'], 'Include unsuccessful attempts when evaluating completed-task economics.', 'Define success before running the comparison.'),
('Subscription and API billing', 'compare', ['Subscription plan', 'Plan price and limits', 'API access', 'Usage-based charges'], 'A subscription price and an API price describe different products.', 'Do not convert subscription access into an invented per-token rate.'),
('Price comparison assumptions', 'stack', ['Currency', 'Billing date', 'Endpoint', 'Input and output usage', 'Other charges'], 'Comparable cost estimates need an explicit common basis.', 'Taxes, discounts, and cached input may change the final invoice.'),
('A bounded test budget', 'gate', ['Planned tests', 'Within approved budget?', 'Run selected tests', 'Reduce or defer', 'Record spending'], 'Control the cost of collecting comparison evidence.', 'A budget limit is not permission to fabricate unrun tests.'),
('Retries and cumulative cost', 'flow', ['Initial attempt', 'Failed outcome', 'Additional attempt', 'Combined cost'], 'Retries can increase the cost of producing one usable result.', 'Track each billed attempt rather than only the final answer.'),
('Cached input affects billing', 'split', ['Input usage', 'Eligible cached input', 'Fresh input', 'Applicable cost record'], 'Classify cached input according to the service’s actual usage report.', 'Do not assume every repeated request qualifies for caching.'),
('Savings require a baseline', 'compare', ['Baseline workflow', 'Measured task cost', 'Alternative workflow', 'Measured task cost'], 'Savings compare two named workflows for an equivalent task.', 'State quality tradeoffs and whether the costs are measured or estimated.'),
('Choosing affordable adequacy', 'gate', ['Candidate model', 'Meets task requirements?', 'Consider cost and latency', 'Reject for this task', 'Task-specific choice'], 'Choose among options that satisfy the task rather than price alone.', 'Passing a small test does not prove broad equivalence.'),
]),
('Latency and user experience', [
('Where response time is spent', 'flow', ['Network request', 'Provider handling', 'Generation', 'Client rendering'], 'End-to-end time includes more than model generation.', 'Measure the actual user workflow; provider details may be unavailable.'),
('First output and completion time', 'compare', ['First visible output', 'Waiting begins to ease', 'Completed answer', 'Full task response'], 'Time to first output and total completion time measure different events.', 'Fast initial text can still precede a slow or incomplete answer.'),
('Latency with tools', 'flow', ['Model response', 'Tool call', 'Tool result', 'Model follow-up', 'Final output'], 'External tool steps can add time to the interaction.', 'Record tool configuration when comparing response times.'),
('Serial and parallel work', 'compare', ['Serial work', 'One dependency after another', 'Parallel work', 'Independent operations overlap'], 'Independent work can overlap while dependent work must retain order.', 'Concurrency may introduce provider limits and coordination overhead.'),
('Speed and usefulness', 'triangle', ['Response time', 'Task success', 'Total cost'], 'A useful comparison considers speed together with quality and cost.', 'Avoid a speed winner whose response fails the task.'),
('Repeated latency measurements', 'matrix', ['Same task', 'Same settings', 'Repeated runs', 'Recorded timing', 'Failure labels', 'Summary range'], 'Measure a distribution rather than relying on one unusually fast run.', 'Network conditions and service load can affect observations.'),
('Perceived responsiveness', 'hub', ['User experience', 'Visible progress', 'Streaming output', 'Clear error state', 'Interrupt controls', 'Usable final answer'], 'Responsive interfaces communicate progress and handle interruption.', 'Perceived responsiveness and measured speed are different.'),
('A task with a deadline', 'gate', ['User task', 'Can finish in time?', 'Return useful result', 'Stop or qualify', 'Deadline-aware outcome'], 'A response is useful only if it meets the task’s timing needs.', 'Define what counts as acceptable partial work before evaluation.'),
('Measuring through the interface', 'flow', ['User submits', 'First visible result', 'Usable completion', 'Timing record'], 'Product comparisons should measure what the viewer actually experiences.', 'Record interface and plan because they can affect behavior.'),
('Latency evidence and extrapolation', 'compare', ['Observed runs', 'Measured conditions', 'General claim', 'Needs broader evidence'], 'A few response-time observations support a narrow conclusion.', 'Do not present limited measurements as a universal provider ranking.'),
]),
('Evaluation design', [
('A practical evaluation plan', 'flow', ['Viewer task', 'Success rubric', 'Representative inputs', 'Run comparisons', 'Interpret results'], 'Define the evaluation before seeing which model wins.', 'Choose tasks that resemble the intended viewer use.'),
('Correctness and usefulness', 'compare', ['Correctness', 'Facts or behavior match', 'Usefulness', 'Task needs are met'], 'An accurate answer can still be poorly suited to the task.', 'Score each relevant dimension explicitly.'),
('A rubric for original outputs', 'stack', ['Required facts', 'Instruction compliance', 'Reasoning support', 'Output usability', 'Critical failures'], 'Use a stated rubric to compare generated outputs consistently.', 'Weights and failure rules should match the intended task.'),
('Automated and human checks', 'merge', ['Deterministic checks', 'Human assessment', 'Evidence review', 'Combined evaluation'], 'Different checks identify different kinds of failures.', 'Document disagreement rather than forcing an unsupported score.'),
('Development and held-out tests', 'compare', ['Development inputs', 'Guide prompt revision', 'Held-out inputs', 'Assess generalization'], 'Separate examples used to improve a workflow from later evaluation.', 'Do not quietly reuse held-out results to tune the same comparison.'),
('A failure taxonomy', 'matrix', ['Wrong fact', 'Missed instruction', 'Invalid format', 'Unsupported citation', 'Tool failure', 'Incomplete work'], 'Label failure modes so viewers understand why an output failed.', 'Define categories and allow multiple failures when appropriate.'),
('Blind output review', 'flow', ['Saved outputs', 'Hide model identity', 'Apply common rubric', 'Reveal identities'], 'Blinded review reduces some expectations tied to brand or price.', 'Blinding does not remove all reviewer bias.'),
('A model judge with oversight', 'gate', ['Judge assessment', 'Matches evidence?', 'Use qualified score', 'Human review', 'Recorded verdict'], 'A model-based judgment requires checks and documented limitations.', 'A judge can favor style or share errors with the evaluated model.'),
('Task performance and generalization', 'compare', ['Observed task results', 'Evidence in test scope', 'Broad ability claim', 'Requires broader coverage'], 'Results apply most directly to the conditions that were evaluated.', 'Do not claim universal superiority from a narrow suite.'),
('Evaluation records that can be rerun', 'hub', ['Reproducible test', 'Prompt and files', 'Model identity', 'Settings', 'Raw outputs', 'Scoring procedure'], 'Save what is needed to inspect or repeat the comparison.', 'Hosted model behavior can change even when a public name stays the same.'),
]),
('Uncertainty and fair interpretation', [
('One run versus repeated runs', 'compare', ['Single response', 'One observed outcome', 'Repeated responses', 'Observed variability'], 'Repeated runs reveal variation hidden by one example.', 'Choose repetitions according to stakes, variability, and budget.'),
('Sample and target population', 'funnel', ['Possible viewer tasks', 'Selected sample', 'Observed results', 'Scoped conclusion'], 'A tested sample may not represent all tasks viewers perform.', 'Explain selection and avoid overgeneralizing its results.'),
('A score needs a denominator', 'stack', ['Metric definition', 'Number tested', 'Successes and failures', 'Reported score'], 'A score is interpretable only with its metric and test scope.', 'Do not hide exclusions that change the denominator.'),
('Uncertainty in a ranking', 'compare', ['Observed scores', 'Difference between scores', 'Uncertainty estimate', 'Precision of the comparison'], 'Small observed score differences may not justify a ranked winner.', 'Use source-provided uncertainty or a justified analysis method.'),
('No observed difference', 'compare', ['Similar observed results', 'Limited test evidence', 'Proven equivalence', 'Requires an equivalence design'], 'A failure to observe a difference is not proof of equivalence.', 'State the limits of the sample and method.'),
('Selection bias in examples', 'gate', ['Candidate examples', 'Chosen before outcomes?', 'Use representative set', 'Disclose selection', 'Honest demonstration'], 'Choosing only impressive outcomes can distort the comparison.', 'Predefine selection or disclose how shown examples were chosen.'),
('Repeated reports from one origin', 'tree', ['Original result', 'Secondary report A', 'Secondary report B', 'Cites original result', 'Cites original result'], 'Several reports can repeat the same underlying evidence.', 'Count independent evidence rather than article volume.'),
('Correlation and task explanation', 'compare', ['Scores move together', 'Observed association', 'One causes the other', 'Needs causal evidence'], 'Related benchmark scores do not establish a causal explanation.', 'Use associations cautiously when explaining practical outputs.'),
('Missing data and a fair verdict', 'gate', ['Comparison record', 'Critical fields known?', 'Interpret within scope', 'Mark not comparable', 'Qualified conclusion'], 'Missing settings or methods can prevent a fair score comparison.', 'Unknown data should remain unknown rather than being filled in.'),
('Multiple comparisons', 'hub', ['Comparison campaign', 'Many tasks', 'Many models', 'Several metrics', 'Selection effects', 'Scoped conclusions'], 'Large comparison campaigns create more opportunities for chance patterns.', 'Prespecify key outcomes and disclose exploratory findings.'),
]),
('Benchmark literacy', [
('What a benchmark establishes', 'triangle', ['Defined test', 'Specified setup', 'Observed metric'], 'A benchmark result describes a test under a particular setup.', 'It does not establish universal intelligence or superiority.'),
('Benchmark version matters', 'compare', ['Benchmark release A', 'Tasks and scoring A', 'Benchmark release B', 'Tasks and scoring B'], 'Different releases can contain different tests or scoring rules.', 'Compare versions only when their relationship is documented.'),
('Model and system benchmarks', 'compare', ['Model evaluation', 'Model plus specified inputs', 'System evaluation', 'Model plus tools and agent'], 'A complete agent system is different from an isolated model.', 'Record tools, prompts, retries, and scaffolding.'),
('A benchmark’s measured skill', 'flow', ['Benchmark task', 'Scoring rule', 'Measured dimension', 'Viewer implication'], 'Explain what the test measures before using the score.', 'Also explain important task abilities the benchmark does not measure.'),
('Knowledge and reasoning tests', 'compare', ['Knowledge tasks', 'Use learned information', 'Reasoning tasks', 'Solve specified problems'], 'Different tests emphasize different mixtures of knowledge and reasoning.', 'Do not assume a benchmark cleanly isolates a single ability.'),
('Coding snippets and repository changes', 'compare', ['Standalone coding', 'Solve bounded problem', 'Repository work', 'Inspect and repair project'], 'Coding problem tests and repository tasks assess different workflows.', 'Agent tools and test infrastructure matter for repository results.'),
('Preference and correctness', 'compare', ['Human preference', 'Which response is favored', 'Task correctness', 'Which response is right'], 'A preferred answer is not automatically the more correct answer.', 'Interpret preference scores according to their evaluation design.'),
('Contamination risk', 'cycle', ['Public test content', 'Potential training exposure', 'Evaluation result', 'Interpretation caution'], 'Exposure to evaluation material can complicate score interpretation.', 'Potential exposure is not proof that contamination occurred.'),
('Benchmark saturation', 'funnel', ['Many tested models', 'Similar high scores', 'Less separation', 'Need complementary tasks'], 'A test that barely separates models may be less useful for choosing.', 'Assess discrimination with evidence rather than a fixed score threshold.'),
('A benchmark coverage map', 'matrix', ['Knowledge', 'Reasoning', 'Coding', 'Tool use', 'Long-context work', 'Multimodal tasks'], 'Use several relevant dimensions instead of one universal leaderboard.', 'Coverage categories are illustrative; choose tests for actual viewer tasks.'),
]),
('Model comparisons', [
('The same-prompt comparison', 'split', ['Identical task input', 'Cloud model A', 'Cloud model B', 'Common scoring rubric'], 'Compare outputs using the same task and stated success criteria.', 'Record differing system instructions and endpoint behavior.'),
('Equivalent settings are explicit', 'stack', ['Exact model identity', 'Reasoning setting', 'Tool access', 'Generation limits', 'Test date'], 'State the settings that could meaningfully change each result.', 'Identical setting names across providers may not mean identical behavior.'),
('Two complementary comparison modes', 'compare', ['Controlled configuration', 'Isolate selected variables', 'Best practical workflow', 'Compare complete solutions'], 'Controlled tests and practical system comparisons answer different questions.', 'Label the mode and avoid mixing their rankings.'),
('A complete comparison panel', 'hub', ['Viewer decision', 'Prompt', 'Actual output', 'Exact model', 'Task cost', 'Relevant benchmark'], 'Show the task, result, model, cost, and benchmark evidence together.', 'The practical output illustrates behavior; it does not validate a benchmark.'),
('A cheap model’s failure boundary', 'gate', ['Cheaper candidate', 'Meets this task?', 'Use with stated limits', 'Choose stronger alternative', 'Task-specific decision'], 'Show when a lower-cost option succeeds and when it falls short.', 'Do not infer broader equivalence from a few successes.'),
('Best result and best value', 'compare', ['Best observed result', 'Highest task score', 'Best observed value', 'Adequate result at lower cost'], 'The highest score and the best purchase can be different judgments.', 'Define adequacy and the cost basis before naming value.'),
('A comparison with unavailable evidence', 'gate', ['Candidate comparison', 'Evidence available?', 'Use verified results', 'Mark untested', 'Scoped recommendation'], 'Unavailable access should remain visible in the comparison record.', 'Never fabricate actual model outputs or benchmark values.'),
('Updating a comparison after change', 'cycle', ['Recorded baseline', 'Verified change', 'Relevant rerun', 'Updated recommendation'], 'Rerun the parts affected by a model or platform change.', 'Old results must remain dated rather than silently overwritten.'),
('Output excerpts and full records', 'compare', ['On-screen excerpt', 'Readable demonstration', 'Full saved output', 'Audit and replication'], 'A short excerpt can illustrate a result while the full record preserves context.', 'Mark omissions and avoid excerpts that reverse the overall meaning.'),
('An honest ranked shortlist', 'funnel', ['Tested candidates', 'Task-qualified options', 'Quality-cost evidence', 'Scoped shortlist'], 'Rank only the candidates supported by comparable evidence.', 'A shortlist is not an exhaustive global leaderboard.'),
]),
('Evidence and asset provenance', [
('The provenance chain', 'flow', ['Original source', 'Captured evidence', 'Verified claim', 'Rendered visual', 'Episode reference'], 'Preserve the source of a claim through the finished episode.', 'A screenshot preserves appearance; verify the underlying claim separately.'),
('An unaltered screenshot and overlays', 'split', ['Source screenshot', 'Preserved original', 'Annotated copy', 'Episode visual'], 'Keep original captures separate from editorial highlights.', 'Annotations must not change the meaning of the original evidence.'),
('A screenshot metadata record', 'stack', ['Source URL', 'Capture date', 'Relevant region', 'Source identity', 'Reuse notes'], 'Store enough information to identify and inspect a captured source.', 'Visibility on the web does not establish permission to redistribute.'),
('Chart data before chart design', 'flow', ['Verified values', 'Units and metric', 'Chart specification', 'Rendered chart'], 'Use verified structured data for accurate comparison graphics.', 'Never recreate data labels from an unverified guess.'),
('Evidence and decorative artwork', 'compare', ['Evidence asset', 'Supports a factual claim', 'Decorative asset', 'Supports presentation style'], 'Differentiate evidentiary visuals from illustrations.', 'Decorative art must not be mistaken for a real benchmark or product capture.'),
('Licensing and factual accuracy', 'compare', ['Reuse rights', 'Can the asset be used?', 'Factual support', 'Does the claim hold?'], 'Permission to reuse an asset and accuracy of its content are separate checks.', 'Record both checks without assuming one proves the other.'),
('A claim affected by a correction', 'tree', ['Corrected evidence', 'Affected claim A', 'Affected claim B', 'Revise scene and script A', 'Revise index and visual B'], 'Track which outputs depend on changed evidence.', 'Preserve correction history and identify what was updated.'),
('Evergreen and time-sensitive content', 'compare', ['Evergreen explanation', 'Stable conceptual guidance', 'Current evidence', 'Prices, releases, and results'], 'Store reusable concepts separately from facts that need rechecking.', 'Even conceptual explanations should be reviewed when reused.'),
('An audit-ready episode package', 'hub', ['Episode record', 'Sources', 'Captures', 'Prompts', 'Raw outputs', 'Calculations'], 'Keep the evidence behind an episode organized and inspectable.', 'Exclude secrets, private user data, and unauthorized media.'),
('A dated recommendation index', 'flow', ['Episode evidence', 'Task recommendation', 'Date and limitations', 'Searchable entry'], 'A comparison index helps viewers locate supported choices by task.', 'Mark superseded recommendations when relevant evidence changes.'),
]),
('Reliability and trustworthy use', [
('Reliability as a complete workflow', 'triangle', ['Model output', 'Application controls', 'Verification'], 'Reliable use requires more than selecting a strong model.', 'The required verification depends on the consequences of error.'),
('Critical failures in an evaluation', 'gate', ['Generated answer', 'Critical error present?', 'Fail this task', 'Score other criteria', 'Recorded outcome'], 'Some failures should outweigh polish or partial correctness.', 'Define critical failures before seeing model outputs.'),
('Fallback after an unusable result', 'flow', ['Initial response', 'Failed checks', 'Permitted fallback', 'Verified final result'], 'A fallback can handle failures while preserving a clear cost record.', 'Account for all attempts and avoid hiding the initial failure.'),
('Prompt injection in retrieved content', 'gate', ['External content', 'Attempts to redirect?', 'Reject injected instruction', 'Inspect task evidence', 'Apply app controls'], 'Retrieved content can contain attempts to redirect the workflow.', 'Detection can miss attacks; apply controls to all external content.'),
('Privacy boundaries in demonstrations', 'stack', ['Public test inputs', 'Synthetic identities', 'No account secrets', 'Redacted captures', 'Shareable evidence'], 'Use demonstration material that can be safely shown to viewers.', 'Redaction must be checked in exported files as well as source files.'),
('A release status ladder', 'ladder', ['Announced', 'Limited access', 'Generally available', 'Deprecated or retired'], 'Release states describe access and lifecycle, not performance.', 'Possible stages; not every release follows every stage. Verify current status.'),
('Availability varies by access route', 'hub', ['Cloud access', 'Web application', 'API endpoint', 'Account plan', 'Region', 'Provider hosting'], 'The same model family may be exposed differently across services.', 'Record exact access route and actual feature availability.'),
('A useful limitations disclosure', 'stack', ['What was tested', 'What was unavailable', 'Known failures', 'Uncertain claims', 'Scope of conclusion'], 'Limitations should help viewers judge whether results apply to them.', 'Avoid generic caveats that hide a specific missing verification.'),
('An answer that admits a gap', 'gate', ['Viewer question', 'Verified support exists?', 'Answer with support', 'State missing evidence', 'Offer useful next step'], 'A clear evidence gap is more useful than an invented fact.', 'Do not make an untested result look like a tested demonstration.'),
('Closing the loop on quality', 'cycle', ['Published comparison', 'Viewer feedback', 'Evidence review', 'Correction or improvement'], 'Use feedback to identify unclear explanations and factual problems.', 'Feedback guides review; popularity does not establish accuracy.'),
]),
('Robustness on real tasks', [
('A paraphrase robustness test', 'split', ['Same intended task', 'Original wording', 'Equivalent paraphrase', 'Compare task success'], 'Test whether harmless wording changes affect task completion.', 'Verify that paraphrases preserve the actual task requirements.'),
('Irrelevant information in context', 'compare', ['Focused input', 'Relevant evidence only', 'Distractor input', 'Relevant plus irrelevant text'], 'Compare performance with and without task-irrelevant material.', 'Keep the required evidence unchanged when adding distractors.'),
('A multilingual task comparison', 'split', ['Equivalent task', 'Language A', 'Language B', 'Common outcome rubric'], 'Evaluate the languages viewers actually use for the task.', 'Translation can change nuance; validate task equivalence.'),
('Small and complex task instances', 'compare', ['Simple instance', 'Fewer interacting requirements', 'Complex instance', 'More interacting requirements'], 'Task complexity can expose failures absent from simpler examples.', 'Define complexity with concrete task properties, not arbitrary labels.'),
('A follow-up consistency test', 'cycle', ['Initial question', 'Initial answer', 'Relevant follow-up', 'Check retained constraints'], 'Test whether a conversation preserves important requirements across turns.', 'Record the history supplied by the app at each turn.'),
('Error recovery on a tool task', 'split', ['Same task setup', 'Tool succeeds', 'Tool returns error', 'Compare honest recovery'], 'A useful workflow should handle tool failure without inventing success.', 'Keep injected failures separate from real provider outages.'),
('A format robustness check', 'matrix', ['Readable prose', 'Valid structured data', 'Required sections', 'Correct units', 'Usable file', 'No silent truncation'], 'Verify the output format under representative inputs.', 'Format checks complement content evaluation rather than replacing it.'),
('An adversarial instruction test', 'gate', ['Untrusted task content', 'Redirects the task?', 'Maintain authorized goal', 'Use relevant task data', 'Check final behavior'], 'Test whether hostile content changes the workflow’s permitted behavior.', 'Passing a small attack set is not proof of complete security.'),
('A robustness test matrix', 'matrix', ['Prompt variation', 'Context variation', 'Language variation', 'Tool failures', 'Task complexity', 'Conversation follow-ups'], 'Cover the kinds of variation likely to matter in everyday use.', 'Select a manageable test set with explicit scope and held-out examples.'),
('Robustness and universal claims', 'compare', ['Tested variations', 'Observed reliable behavior', 'Every possible input', 'Not established by finite tests'], 'Successful tests establish evidence within their tested conditions.', 'State remaining failure risks without claiming universal reliability.'),
]),
]

assert len(GROUPS) == 18
assert sum(len(items) for _,items in GROUPS) == 180

NAVY='#071424'; PANEL='#102337'; CYAN='#53D9E8'; GOLD='#F5C46B'; WHITE='#F2F6FA'; MUTED='#AAC0D4'

def esc(t): return html.escape(t, quote=True)
def slug(t): return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
def txt(x,y,s,size=28,fill=WHITE,weight=400,anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'
def wrap_lines(s, width=24): return textwrap.wrap(s,width=width,break_long_words=False,break_on_hyphens=False)
def multi(x,y,s,width=24,size=28,fill=WHITE,weight=500,anchor='middle'):
    lines=wrap_lines(s,width)
    return ''.join(txt(x,y+(i-(len(lines)-1)/2)*size*1.28,l,size,fill,weight,anchor) for i,l in enumerate(lines))
def rect(x,y,w,h,fill=PANEL,stroke='#2B4963',r=22,sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def node(x,y,w,h,label,i=0,kind='box'):
    c=CYAN if i%2==0 else GOLD
    if kind=='diamond':
        shape=f'<polygon points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" fill="{PANEL}" stroke="{c}" stroke-width="3"/>'
        wid=20
    else:
        shape=rect(x,y,w,h,stroke=c,sw=2.5)
        shape+=f'<rect x="{x+18}" y="{y+20}" width="5" height="{h-40}" rx="2" fill="{c}"/>'
        wid=max(16,int((w-48)/16))
    return shape+multi(x+w/2,y+h/2+8,label,wid,28,WHITE,600)
def line(x1,y1,x2,y2,color=CYAN,arrow=True,dash=False):
    d=' stroke-dasharray="10 9"' if dash else ''
    m=' marker-end="url(#arrow)"' if arrow else ''
    return f'<path d="M {x1:.1f},{y1:.1f} L {x2:.1f},{y2:.1f}" fill="none" stroke="{color}" stroke-width="4"{d}{m}/>'
def path(d,color=CYAN,dash=False):
    da=' stroke-dasharray="10 9"' if dash else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="4" marker-end="url(#arrow)"{da}/>'

def diagram(style, labels):
    p=[]; n=len(labels)
    if style=='flow':
        w=min(300,1400/n); h=150; gap=58; total=n*w+(n-1)*gap; x=(1920-total)/2; y=510
        for i in range(n-1): p.append(line(x+i*(w+gap)+w,y+h/2,x+(i+1)*(w+gap)-12,y+h/2))
        for i,l in enumerate(labels): p.append(node(x+i*(w+gap),y,w,h,l,i))
    elif style=='merge3':
        poses=[(245,350,515,120),(245,560,515,120),(245,770,515,120),(1210,510,480,220)]
        p.extend([path('M 760,410 L 960,410 L 960,620 L 1198,620'),line(760,620,1198,620),path('M 760,830 L 960,830 L 960,620 L 1198,620')])
        for i,(l,po) in enumerate(zip(labels,poses)):p.append(node(*po,l,i))
    elif style in ('split','merge'):
        if style=='split':
            poses=[(165,530,310,150),(715,360,460,145),(715,670,460,145),(1445,530,310,150)]
            p.extend([path('M 475,605 L 590,605 L 590,432 L 703,432'),path('M 475,605 L 590,605 L 590,742 L 703,742'),path('M 1175,432 L 1290,432 L 1290,605 L 1433,605'),path('M 1175,742 L 1290,742 L 1290,605 L 1433,605')])
        else:
            if n==4:
                poses=[(175,350,430,125),(175,570,430,125),(845,460,370,150),(1440,460,310,150)]
                p.extend([path('M 605,412 L 710,412 L 710,535 L 833,535'),path('M 605,632 L 710,632 L 710,535 L 833,535'),line(1215,535,1428,535)])
            else: raise ValueError('merge expects 4 nodes')
        for i,(l,po) in enumerate(zip(labels,poses)): p.append(node(*po,l,i))
    elif style=='compare':
        x1,x2,w=200,1030,690
        p.append(line(960,330,960,800,MUTED,False,True))
        for i in [0,1]:
            p.append(rect([x1,x2][i],355,w,405,stroke='#365670'))
            p.append(txt([x1,x2][i]+42,403,'DIMENSION '+['A','B'][i],20,[CYAN,GOLD][i],700))
            p.append(multi([x1,x2][i]+w/2,480,labels[i*2],28,36,[CYAN,GOLD][i],700))
            p.append(line([x1,x2][i]+w/2,533,[x1,x2][i]+w/2,575,[CYAN,GOLD][i]))
            p.append(multi([x1,x2][i]+w/2,640,labels[i*2+1],30,28))
    elif style=='stack':
        h=min(92,470/n); gap=22; y=335
        for i,l in enumerate(labels):
            x=340+i*35; w=1240-i*70
            p.append(rect(x,y+i*(h+gap),w,h,stroke=[CYAN,GOLD][i%2]))
            p.append(txt(x+34,y+i*(h+gap)+h/2+10,f'{i+1:02d}',24,[CYAN,GOLD][i%2],700))
            p.append(multi(x+w/2,y+i*(h+gap)+h/2+8,l,55,29))
    elif style=='cycle':
        poses=[(325,345,475,145),(1120,345,475,145),(1120,670,475,145),(325,670,475,145)]
        p.extend([line(800,418,1108,418),line(1358,490,1358,658),line(1120,742,812,742),line(562,670,562,502)])
        p.append(multi(960,591,'REVIEW EACH STEP',22,22,MUTED,600))
        for i,(l,po) in enumerate(zip(labels,poses)): p.append(node(*po,l,i))
    elif style=='hub':
        cx,cy=960,610; outer=labels[1:]; count=len(outer)
        poses=[]
        for i,l in enumerate(outer):
            a=-math.pi/2+i*2*math.pi/count
            x=cx+640*math.cos(a)-185; y=cy+210*math.sin(a)-57
            poses.append((x,y,370,114,l))
            p.append(line(cx,cy,x+185,y+57,MUTED,False))
        p.append(node(cx-235,cy-86,470,172,labels[0],0))
        for i,po in enumerate(poses): p.append(node(*po,i+1))
    elif style=='matrix':
        cols=3 if n==6 else 2; rows=math.ceil(n/cols); w=460 if cols==3 else 680; h=185; gx=48; gy=58
        x=(1920-(cols*w+(cols-1)*gx))/2; y=360
        for i,l in enumerate(labels):
            r,c=divmod(i,cols); xx=x+c*(w+gx); yy=y+r*(h+gy)
            p.append(rect(xx,yy,w,h,stroke=[CYAN,GOLD][i%2]))
            p.append(txt(xx+25,yy+43,f'{i+1:02d}',22,[CYAN,GOLD][i%2],700))
            p.append(multi(xx+w/2,yy+h/2+18,l,25 if cols==3 else 34,30,WHITE,600))
    elif style=='gate':
        poses=[(190,342,420,135),(750,340,420,145),(1320,342,420,135),(750,670,420,145),(1320,670,420,145)]
        p.extend([line(610,409,738,409),line(1170,412,1308,412),line(960,485,960,658,GOLD),path('M 1170,742 L 1308,742',GOLD),path('M 1530,477 L 1530,658')])
        p.append(txt(1235,386,'YES',20,CYAN,700,'middle'));p.append(txt(990,583,'NO',20,GOLD,700))
        # Each gate title is phrased as a condition; labels 2/3 are yes/no paths.
        for i,(l,po) in enumerate(zip(labels,poses)): p.append(node(*po,l,i,kind='diamond' if i==1 else 'box'))
    elif style=='triangle':
        poses=[(710,335,500,145),(255,675,500,145),(1165,675,500,145)]
        p.extend([line(755,416,555,658,MUTED,False),line(1165,416,1365,658,MUTED,False),line(755,748,1165,748,MUTED,False)])
        p.append(multi(960,617,'CONSIDER TOGETHER',24,22,MUTED,600))
        for i,(l,po) in enumerate(zip(labels,poses)): p.append(node(*po,l,i))
    elif style=='tree':
        poses=[(710,330,500,130),(275,545,530,130),(1115,545,530,130),(275,745,530,125),(1115,745,530,125)]
        p.extend([path('M 960,460 L 960,500 L 540,500 L 540,533'),path('M 960,460 L 960,500 L 1380,500 L 1380,533'),line(540,675,540,733),line(1380,675,1380,733)])
        for i,(l,po) in enumerate(zip(labels,poses)): p.append(node(*po,l,i))
    elif style=='funnel':
        ws=[1380,1080,780,480]; y=330; h=100; gap=32
        for i,l in enumerate(labels):
            w=ws[i]; x=(1920-w)/2; yy=y+i*(h+gap)
            if i<n-1:p.append(line(960,yy+h,960,yy+h+gap-12))
            p.append(node(x,yy,w,h,l,i))
    elif style=='ladder':
        for i,l in enumerate(labels):
            x=230+i*330; y=675-i*103
            p.append(node(x,y,420,125,l,i))
            if i<n-1:p.append(path(f'M {x+420},{y+62} L {x+465},{y+62} L {x+465},{y-42} L {x+330-12},{y-42}'))
    else: raise ValueError(style)
    return ''.join(p)

def build():
    records=[]; counter=0
    for gi,(category,items) in enumerate(GROUPS):
        for title,style,labels,subtitle,note in items:
            counter+=1; ident=f'tech-{counter:03d}-{slug(title)}'; name=ident+'.svg'
            svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" role="img" aria-labelledby="title desc">'
                 f'<title id="title">{esc(title)}</title><desc id="desc">{esc(subtitle+" "+note)}</desc>'
                 '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M 0 0 L 9 4.5 L 0 9 Z" fill="#53D9E8"/></marker></defs>'
                 f'<rect width="1920" height="1080" fill="{NAVY}"/>'
                 f'<circle cx="1800" cy="110" r="310" fill="#0C263B" opacity="0.5"/>'
                 f'<path d="M 100 315 H 1820" stroke="#274359" stroke-width="2"/>'
                 +txt(100,85,'AI UPDATE SOURCES  /  EVERGREEN SCHEMATIC',20,CYAN,700)
                 +txt(1820,85,f'{counter:03d} / 180',20,MUTED,600,'end')
                 +txt(100,167,title,49,WHITE,700)
                 +txt(100,229,subtitle,27,MUTED)
                 +txt(100,285,category.upper(),18,GOLD,700)
                 +diagram(style,labels)
                 +'<path d="M 100 922 H 1820" stroke="#274359" stroke-width="2"/>'
                 +multi(100,964,note,110,23,MUTED,400,'start')
                 +txt(100,1030,'Original explanatory graphic • Not measured benchmark evidence • CC BY 4.0',19,MUTED)
                 +txt(1820,1030,'Attribution: AI Update Sources',19,MUTED,400,'end')+'</svg>')
            dest=ASSETS/name; dest.write_text(svg,encoding='utf-8')
            records.append({'id':ident,'title':title,'path':str(dest.relative_to(ROOT)),'category':category,'tags':['cloud-ai','evergreen','technical-diagram',slug(category),style],'intended_use':subtitle,'dimensions':{'width':1920,'height':1080},'kind':'evergreen-diagram','origin':'original','source_urls':[],'license':'CC-BY-4.0','attribution':'AI Update Sources','description':note,'caveat':'Original conceptual schematic; simplifies platform-specific behavior. Verify technical claims and current service details for each episode. Not empirical model or benchmark evidence.','composition':style,'sha256':hashlib.sha256(svg.encode()).hexdigest()})
    (ROOT/'manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    (ROOT/'topics.md').write_text('# 180 original cloud-AI diagrams\n\n'+ '\n'.join(f"- **{r['id']}** — {r['title']} ({r['category']}; {r['composition']})" for r in records)+'\n',encoding='utf-8')
    (ROOT/'README.md').write_text('''# Original cloud-AI technical diagrams

180 original 1920 × 1080 SVG schematics for recurring AI episodes.

These assets explain stable concepts: cloud inference, prompting, context,
tools, search, files, multimodal tasks, platform features, costs, latency,
evaluation, uncertainty, benchmarks, comparisons, provenance, and reliability.
They contain no invented benchmark results, empirical price data, company
logos, or local hosting advice. Each concept is individually labeled and
cataloged in `manifest.json` and `topics.md`.

## Use

SVGs have no external dependencies or embedded scripts. They use editable
vector shapes and text with common fonts. Prefer importing into a presentation
as SVG; verify font substitution in the target application. A conceptual
schematic should be labeled as an illustration, not used as score evidence.

## Rebuild

Run `python generate_diagrams.py` to regenerate all SVGs and metadata.
Run `python generate_diagrams.py --qa` with Pillow and Inkscape available to
render every asset and produce nine contact sheets. `qa/validation.json`
records programmatic checks. The thumbnail renders are QA derivatives of
these 180 assets, not additional unique assets.

## Interpretation

Diagrams simplify real implementations. Verify technical claims and the
current behavior of the exact cloud service before episode use. Node order
does not imply a vendor's documented architecture. No asset asserts a live
model score, current price, current availability, or guaranteed behavior.

## License

Original graphics and generator: CC BY 4.0.
Attribution: **AI Update Sources**.
License: https://creativecommons.org/licenses/by/4.0/
''',encoding='utf-8')
    return records

def qa(records):
    from PIL import Image,ImageDraw,ImageFont
    import xml.etree.ElementTree as ET
    results=[]
    def render(rec):
        src=ROOT/rec['path']; dst=QA/(rec['id']+'.png')
        root=ET.fromstring(src.read_text())
        if root.attrib.get('viewBox')!='0 0 1920 1080':raise ValueError('wrong viewbox')
        subprocess.run(['inkscape',str(src),'--export-type=png','--export-width=480','--export-filename='+str(dst)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
        with Image.open(dst) as im:
            if im.size!=(480,270):raise ValueError('wrong render dimensions')
        return {'id':rec['id'],'svg_parse':'pass','render':'pass','dimensions':'pass'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        results=list(ex.map(render,records))
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
    for idx in range(0,len(records),20):
        page=Image.new('RGB',(2000,1540),'#081424'); draw=ImageDraw.Draw(page)
        for j,rec in enumerate(records[idx:idx+20]):
            x=(j%4)*500+10; y=(j//4)*308+10
            with Image.open(QA/(rec['id']+'.png')) as im:page.paste(im,(x,y))
            draw.text((x+8,y+276),f"{idx+j+1:03d} {rec['title'][:55]}",font=font,fill='white')
        page.save(QA/f'contact-sheet-{idx//20+1:02d}.jpg',quality=92)
    validation={'asset_count':len(records),'unique_titles':len({r['title'] for r in records}),'unique_hashes':len({r['sha256'] for r in records}),'categories':len(GROUPS),'composition_types':len({r['composition'] for r in records}),'render_engine':'Inkscape','all_rendered':True,'checks':results}
    (QA/'validation.json').write_text(json.dumps(validation,indent=2))
    print(json.dumps({k:v for k,v in validation.items() if k!='checks'}))

if __name__=='__main__':
    import sys
    records=build()
    print(f'Generated {len(records)} original SVG assets.')
    if '--qa' in sys.argv:qa(records)
