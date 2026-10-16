# TRELLIS.2 AWS hosting and inference costs

2026-10-16. Research and proposed deployment path, not deployment or spending authorization. Use an on-demand GPU worker that shuts down between working sessions, rather than an always-on endpoint. GPU rental can be modest at our volume; dependency licensing and conversion into a usable actor remain separate prerequisites.

## Verified compute prices

Linux On-Demand list rates in USD before tax, storage and networking. The [official AWS price feed](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2.json) was retrieved directly; its publication timestamp is 2026-10-15T19:13:16Z. [Selected rate records](aws-prices.json) retain rate codes, manifest and decoded source digest. Calculations use 730 hours for an illustrative always-on month, not a fixed AWS monthly charge.

| Instance | GPU memory | Host RAM | Northern Virginia hourly | 20 billed hours | 730 billed hours |
| --- | --- | --- | --- | --- | --- |
| g6.2xlarge | L4, 24 GB | 32 GiB | $0.97760 | $19.55 | $713.65 |
| g5.2xlarge | A10G, 24 GB | 32 GiB | $1.21200 | $24.24 | $884.76 |
| g6e.2xlarge | L40S, 48 GB | 64 GiB | $2.24208 | $44.84 | $1,636.72 |

[AWS G6 specifications](https://aws.amazon.com/ec2/instance-types/g6/), [G5 specifications](https://aws.amazon.com/ec2/instance-types/g5/), [G6e specifications](https://aws.amazon.com/ec2/instance-types/g6e/). Canada Central lists g6.2xlarge at $1.08547/hour and g5.2xlarge at $1.34573/hour. There is no g6e.2xlarge entry in that region in this retrieved feed; absence is not an account-capacity test. Region, GPU quota and live capacity must be checked before deployment. No account-specific entitlement or quota was inspected.

TRELLIS.2 documents Linux, an NVIDIA GPU with at least 24 GB memory, and tested A100/H100 hardware. Its published 3/17/60-second generation timings are H100 measurements, not measurements on these cheaper AWS GPUs, and not our full cold-start/export/Blender turnaround. The 24 GB options are candidates, not qualified deployments. [Official requirements and benchmarks](https://github.com/microsoft/TRELLIS.2).

For the first AWS qualification I would use 48 GB to reduce memory pressure as a confound, then test the 24 GB worker against the same inputs and settings. Retain the cheaper worker only if it preserves quality and improves total cost. Higher hourly price can still yield a lower cost per successful job if it avoids failures or finishes sufficiently faster.

## What a generation actually costs

GPU cost = hourly rate × total billed instance seconds / 3600. Instance uptime includes loading, preprocessing, inference, export, failed attempts and idle gaps. Startup billing and rounding follow [EC2 billing terms](https://aws.amazon.com/ec2/pricing/on-demand/); warm inference is only one component.

Illustration, not a runtime prediction: if an entire warm generation/export takes three minutes, compute is about $0.049 on g6.2xlarge or $0.112 on g6e.2xlarge. If boot/loading plus ten such generations occupy 45 billed minutes, the session costs $0.73 or $1.68, respectively, before other services. Rejected outputs still cost money.

Allow storage and network costs separately. At the $0.08/GB-month rate illustrated by [AWS gp3 pricing](https://aws.amazon.com/ebs/pricing/), a retained 100 GB disk costs $8/month even while its instance is stopped; verify the selected regional rate and actual disk size before launch. Add container-image storage, private S3 artifacts/model cache, logs, snapshots and transfers. A provisional $10–20/month ancillary allowance is a planning placeholder for a small retained footprint, not a quoted bill or ceiling. Large assets, retained versions or network infrastructure can exceed it.

With 20 total billed GPU hours and that allowance, an illustrative month is approximately $30–40 on L4 or $55–65 on L40S. Initial dependency compilation, setup failures and adaptation effort are additional; development tokens/time are not included. Ten or forty hours scale the compute component linearly. No minimum subscription is necessary for On-Demand EC2, but retained storage can keep accruing costs.

Avoid an always-on load balancer/NAT gateway for the initial test. An ephemeral public IPv4 address with no inbound access and SSM outbound management is one possible low-overhead design; private networking is another with its own endpoint/NAT costs. The former is not a publicly exposed model service. AWS charges $0.005/hour for both in-use and idle public IPv4 addresses, so release unused allocations. [VPC pricing](https://aws.amazon.com/vpc/pricing/). The final network design requires a scoped security review, not a cost-only choice.

## Deployment path if quality warrants it

1. **Clear the actual execution stack.** Bind core/weights/dependency versions and licenses, preprocessing, inference and export. Prove a route that can legally serve the intended production; the standard stack has unresolved restrictions described below.
2. **Qualify one temporary EC2 worker.** Pin a Linux/CUDA container or image, model weights and settings; keep installation/build separate from inference measurements. Submit a few representative inputs, first at moderate resolution, and measure peak GPU/host memory, cold-start, warm inference, mesh export, failures and Blender import. Confirm that useful shape/detail survives conversion into required editable/performance components. No rig, groom or actor acceptance follows from a successful GLB export.
3. **Use work sessions before building a service.** Start once, run several variations while weights remain loaded, write outputs and receipts to private S3, then stop automatically. Cache large weights on an encrypted volume if that saves more than the retained-storage cost. Keep accepted outputs and job truth outside the disposable worker. A worker crash may lose an unfinished sample, not accepted production state.
4. **Integrate a queued Factory capability only after the proof.** Factory submits an immutable request containing input hashes, model/container revisions, seed, resolution, export settings and a budget reservation. A GPU worker returns meshes/materials, logs, hashes and timings. Local Blender remains the next stage. Use AWS Batch with EC2 GPU compute and scale-to-zero as a candidate implementation; AWS Batch has no additional orchestration fee, but EC2/storage/network charges remain. Start On-Demand; evaluate interruptible Spot only after retries and output publication are idempotent. [Batch GPU support](https://docs.aws.amazon.com/batch/latest/userguide/gpu-jobs.html), [Batch pricing](https://aws.amazon.com/batch/pricing/).

The durable interface is: Factory job → private input artifact → disposable GPU execution → durable result and receipt → Blender conversion/review. TRELLIS.2 is replaceable behind that interface. The first implementation does not need Kubernetes, a public web app, real-time endpoints or a continuously running orchestration server.

SageMaker Asynchronous Inference is a later alternative if managed endpoint operations become useful: it queues requests and supports scaling to zero, but uses its own instance pricing and container contract. Configure wake-from-zero explicitly for low-volume use; otherwise a small queue can wait below the scaling threshold. It is not a promise of instant or zero-overhead inference. [Asynchronous inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html), [scaling details](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference-autoscale.html).

## Licensing prerequisite discovered in this research

The prior open-model shortlist must not be read as commercial clearance. TRELLIS.2 core and weights are advertised under MIT, but its documented setup installs nvdiffrast v0.4.0 and a renderutils branch of nvdiffrec. Both inspected dependency licenses restrict use to noncommercial research/evaluation. The standard o-voxel textured GLB exporter imports and uses nvdiffrast; this is not just a dispensable preview window.

Sources: [setup versions](https://github.com/microsoft/TRELLIS.2/blob/main/setup.sh), [nvdiffrast v0.4.0 license section 3.3](https://github.com/NVlabs/nvdiffrast/blob/v0.4.0/LICENSE.txt), [installed nvdiffrec branch license section 3.3](https://github.com/JeffreyXiang/nvdiffrec/blob/renderutils/LICENSE.txt), [GLB postprocessing code](https://github.com/microsoft/TRELLIS.2/blob/main/o-voxel/o_voxel/postprocess.py).

Commercial production is therefore not cleared through the unmodified stack. Investigate permission or a technically qualified replacement/bypass for restricted components, including background removal; do not assume that simply omitting previews resolves it. Research evaluation and producing monetized movie assets are different uses. These findings do not establish that NVIDIA owns generated characters, or that every possible TRELLIS-based pipeline is prohibited. Complete transitive dependency and output-rights review remains necessary. A freely reachable hosted demo is not a substitute for that review.

## Safeguards and success criteria

No deployment or spending is authorized by this proposal. A future paid test needs an explicit total ceiling, region/input scope and expiry. Use one approved instance type, admission/concurrency limits, no unbounded retries, an independent cloud shutdown watchdog and conservative cost reservations. GPU vCPU limits alone are not a sufficient hard dollar cap. AWS Budgets is a delayed alarm, not an immediate spending circuit breaker. [AWS Budgets timing](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html).

Use temporary IAM roles and least-privilege object prefixes, no embedded AWS/API credentials, encryption, no public model ports, pinned reviewed dependencies and restricted outputs. Treat input assets and generated meshes as data, never executable instructions. Keep scratch retention distinct from the established verified-production-backup policy; a successful S3 result upload does not prove full disaster recovery.

Record per job: model/input/export versions, instance/region, input/output sizes, lifecycle timestamps, cold and warm time, peak memory, retries, technical completion, conversion effort and usable/accepted status. Reconcile estimated job allocations against actual billed instance uptime, including idle/startup, without double counting. Cost per accepted asset, conversion effort and success rate matter more than the smallest isolated inference number. Unknown engineering token consumption remains unknown.

The next useful deliverable is a dependency-cleared, representative image-to-mesh comparison and conversion proof, not infrastructure built around an unqualified generator. If the free evaluation succeeds, produce the minimal AWS execution plan and budget for approval. Reassess if rights cannot be cleared, texture/detail collapses during conversion, or performance requires a materially larger machine. Preserve the source/generator/conversion distinction from284 and the approved Sikh/Pashtun quality floor.

## Knowledge and authority reconciliation

Fresh planning packet: `.runtime/knowledge-pilot213/sikh285-packet.json`; model/actor obligations are preserved, not awarded a visual pass. The bounded pilot does not cover AWS infrastructure, dependency licenses or pricing. This report adds manual source reconciliation; no source pins were changed to bypass missing coverage.

Reviewed full original exchanges in `.runtime/knowledge/ai-movie-production-system-20260917-part01.json`: `95cbeae3-1ddb-4cb1-a8a0-9c4fd1e865e1` confirms dynamic local/remote placement; `995eca96-75e9-497e-a16f-1b15e208b51d` confirms immutable work packages and proposes disposable warm state; `3a952e35-f050-4187-ab39-392a7ab4b119` contains the Director's agreement to that distinction. Reuse these principles; AWS Batch/SageMaker and the instance choices remain proposals, not adopted architecture or present implementation. Reviewed strategy184 and current262/284 research limits. Sikh remains the sole active sequence, failed283 remains failed, and no production asset or release gate advances.

Research completed without AWS account operations, deployment, installations, paid inference, asset uploads, Git push or S3 backup. Planning exchange285; next checkpoint290. The production evidence gate remains blocked by unrun native/visual requirements; this is a research handoff, not an execution or character handoff.
