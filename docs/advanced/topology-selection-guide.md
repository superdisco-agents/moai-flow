# 토폴로지 선택 가이드

> MoAI-Flow 스웜 조정을 위한 최적 토폴로지 선택 전략

---

## 🎯 개요

MoAI-Flow는 5가지 토폴로지 패턴을 제공하여 다양한 작업 특성에 최적화된 다중 에이전트 조정을 지원합니다. 이 가이드는 작업 요구사항에 따라 적절한 토폴로지를 선택하는 방법을 제시합니다.

---

## 📊 토폴로지 비교 요약

| 토폴로지 | 최적 에이전트 수 | 통신 복잡도 | 메시지 지연 | 최적 사용 케이스 |
|----------|-----------------|-------------|-------------|-----------------|
| **Hierarchical** | 10+ | O(log n) | 낮음 | 대규모 조직 구조 |
| **Mesh** | 3-5 | O(n²) | 매우 낮음 | 소규모 협업 |
| **Star** | 5-10 | O(1) | 매우 낮음 | 중앙 집중형 조정 |
| **Ring** | 3-8 | O(n) | 중간 | 파이프라인 워크플로우 |
| **Adaptive** | 가변 | 동적 | 동적 | 변동적인 작업 부하 |

---

## 🏗️ 토폴로지 상세 가이드

### 1. Hierarchical Topology (계층형)

#### 언제 사용하나요?

✅ **사용 권장**:
- 에이전트 수가 10개 이상인 대규모 프로젝트
- 명확한 역할 계층이 필요한 경우 (manager → expert → worker)
- 확장성이 중요한 경우
- 권한 기반 의사결정이 필요한 경우

❌ **사용 비권장**:
- 소규모 팀 (5명 이하)
- 모든 에이전트가 동등한 권한을 가져야 하는 경우
- 실시간 협업이 필수적인 경우

#### 구조

```
         Alfred (Layer 0)
              │
     ┌────────┼────────┐
     │        │        │
  Manager  Manager  Manager (Layer 1)
     │        │        │
  ┌──┼──┐  ┌─┼─┐  ┌──┼──┐
Expert1  Expert2  Expert3 ... (Layer 2)
  │        │        │
Worker1  Worker2  Worker3 ... (Layer 3)
```

#### 성능 특성

- **메시지 지연**: 0.5ms (평균)
- **처리량**: 12,000 msg/s (10 에이전트)
- **확장성**: 우수 (O(log n))
- **장애 허용**: 중간 (부모 노드 실패 시 영향 큼)

#### 코드 예제

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

# Hierarchical 토폴로지 생성
coordinator = SwarmCoordinator(
    topology_type="hierarchical",
    root_agent_id="alfred"
)

# Layer 1: Managers
coordinator.register_agent(
    "manager-spec",
    {"type": "manager", "layer": 1, "parent_id": "alfred"}
)
coordinator.register_agent(
    "manager-tdd",
    {"type": "manager", "layer": 1, "parent_id": "alfred"}
)

# Layer 2: Experts
coordinator.register_agent(
    "expert-backend",
    {"type": "expert", "layer": 2, "parent_id": "manager-tdd"}
)
coordinator.register_agent(
    "expert-frontend",
    {"type": "expert", "layer": 2, "parent_id": "manager-tdd"}
)

# Layer 3: Workers
coordinator.register_agent(
    "worker-test",
    {"type": "worker", "layer": 3, "parent_id": "expert-backend"}
)
```

#### 사용 시나리오

**대규모 마이크로서비스 프로젝트**:
- Alfred → 3명의 Manager (Spec, TDD, Docs)
- Manager → 6명의 Expert (Backend, Frontend, Database, Security, DevOps, Debug)
- Expert → 12명의 Worker (테스트 실행, 문서 생성, 배포 자동화)

---

### 2. Mesh Topology (메시형)

#### 언제 사용하나요?

✅ **사용 권장**:
- 에이전트 수가 3-5개인 소규모 팀
- 긴밀한 협업이 필요한 경우
- 모든 에이전트가 직접 통신해야 하는 경우
- 최소 지연이 중요한 경우

❌ **사용 비권장**:
- 에이전트 수가 6개 이상 (O(n²) 복잡도)
- 네트워크 대역폭이 제한적인 경우
- 중앙 집중식 관리가 필요한 경우

#### 구조

```
Agent1 ◄──► Agent2
  │  ╲      ╱  │
  │   ╲    ╱   │
  │    ╲  ╱    │
  │     ╳      │
  │    ╱  ╲    │
  │   ╱    ╲   │
  │  ╱      ╲  │
Agent3 ◄──► Agent4
```

#### 성능 특성

- **메시지 지연**: 0.3ms (3 에이전트), 0.8ms (5 에이전트)
- **처리량**: 15,000 msg/s (3 에이전트), 8,000 msg/s (5 에이전트)
- **확장성**: 제한적 (O(n²))
- **장애 허용**: 우수 (다중 경로 존재)

#### 코드 예제

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

# Mesh 토폴로지 생성 (기본값)
coordinator = SwarmCoordinator(topology_type="mesh")

# 3-5명의 에이전트 등록
coordinator.register_agent(
    "expert-debug",
    {"type": "expert", "capabilities": ["debugging", "profiling"]}
)
coordinator.register_agent(
    "expert-backend",
    {"type": "expert", "capabilities": ["python", "fastapi"]}
)
coordinator.register_agent(
    "expert-database",
    {"type": "expert", "capabilities": ["postgresql", "redis"]}
)

# 모든 에이전트가 직접 통신 가능
coordinator.send_message(
    "expert-debug",
    "expert-backend",
    {"type": "bug_found", "location": "api/auth.py:142"}
)

# 브로드캐스트 (0.3ms 이내 모두 수신)
coordinator.broadcast_message(
    "expert-debug",
    {"type": "critical_issue", "severity": "high"}
)
```

#### 사용 시나리오

**긴급 버그 수정**:
- 3-4명의 전문가가 실시간으로 협업
- Debug, Backend, Database 전문가가 직접 통신
- 최소 지연으로 빠른 문제 해결

---

### 3. Star Topology (성형)

#### 언제 사용하나요?

✅ **사용 권장**:
- 에이전트 수가 5-10개인 중규모 팀
- 중앙 집중식 조정이 필요한 경우
- 허브가 모든 메시지를 라우팅해도 무방한 경우
- 네트워크 트래픽 모니터링이 필요한 경우

❌ **사용 비권장**:
- 허브 단일 장애점(SPOF)이 허용되지 않는 경우
- P2P 직접 통신이 필수적인 경우
- 허브 병목이 성능 문제가 되는 경우

#### 구조

```
        Hub (Alfred)
        /  │  │  \
       /   │  │   \
    Agent1 │  │ Agent4
          Agent2 Agent3
```

#### 성능 특성

- **메시지 지연**: 0.2ms (5 에이전트), 0.3ms (10 에이전트)
- **처리량**: 18,000 msg/s (5 에이전트), 16,000 msg/s (10 에이전트)
- **확장성**: 좋음 (O(1) 라우팅)
- **장애 허용**: 낮음 (허브 실패 시 전체 중단)

#### 코드 예제

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

# Star 토폴로지 생성 (Alfred가 허브)
coordinator = SwarmCoordinator(
    topology_type="star",
    root_agent_id="alfred"  # 허브 에이전트
)

# 스포크 에이전트 등록
for i in range(1, 8):
    coordinator.register_agent(
        f"worker-{i}",
        {"type": "worker", "task": f"task_{i}"}
    )

# 허브를 통한 메시지 라우팅
coordinator.send_message(
    "worker-1",
    "worker-5",
    {"type": "data", "payload": "processed_data"}
)
# worker-1 → alfred (hub) → worker-5 (2홉)

# 허브가 모든 스포크에 브로드캐스트
coordinator.broadcast_message(
    "alfred",
    {"type": "global_config", "max_threads": 4}
)
```

#### 사용 시나리오

**데이터 처리 파이프라인**:
- Alfred가 허브로 모든 작업 조정
- 7개의 워커가 독립적으로 데이터 처리
- 허브가 결과 수집 및 재분배

---

### 4. Ring Topology (링형)

#### 언제 사용하나요?

✅ **사용 권장**:
- 순차적 처리가 필요한 파이프라인
- 에이전트 간 명확한 작업 순서가 있는 경우
- 데이터 흐름이 단방향 또는 양방향인 경우
- ETL (Extract-Transform-Load) 워크플로우

❌ **사용 비권장**:
- 병렬 처리가 필요한 경우
- 임의의 에이전트 간 통신이 필요한 경우
- 최소 지연이 중요한 경우

#### 구조

```
Agent1 ──► Agent2 ──► Agent3
  ▲                      │
  │                      ▼
Agent5 ◄── Agent4 ◄── Agent6
```

#### 성능 특성

- **메시지 지연**: 1.5ms (평균)
- **처리량**: 6,000 msg/s
- **확장성**: 중간 (O(n) 라우팅)
- **장애 허용**: 중간 (링 재구성 가능)

#### 코드 예제

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator

# Ring 토폴로지 생성
coordinator = SwarmCoordinator(topology_type="ring")

# 순차적으로 에이전트 등록 (등록 순서 = 링 순서)
coordinator.register_agent("extract", {"type": "extractor"})
coordinator.register_agent("transform", {"type": "transformer"})
coordinator.register_agent("validate", {"type": "validator"})
coordinator.register_agent("load", {"type": "loader"})
coordinator.register_agent("report", {"type": "reporter"})

# 순환 링에서 데이터 처리
coordinator.send_message(
    "extract",
    "transform",
    {"data": raw_data, "source": "database"}
)
# extract → transform → validate → load → report → extract (순환)
```

#### 사용 시나리오

**ETL 데이터 파이프라인**:
1. Extract: 데이터베이스에서 데이터 추출
2. Transform: 데이터 변환 및 정제
3. Validate: 데이터 검증
4. Load: 데이터 웨어하우스에 적재
5. Report: 처리 결과 보고

---

### 5. Adaptive Topology (적응형)

#### 언제 사용하나요?

✅ **사용 권장**:
- 작업 부하가 동적으로 변하는 경우
- 에이전트 수가 가변적인 경우
- 최적 토폴로지를 자동으로 선택하고 싶은 경우
- 복잡한 워크플로우가 여러 단계를 거치는 경우

❌ **사용 비권장**:
- 토폴로지 전환 오버헤드가 허용되지 않는 경우
- 고정된 토폴로지가 명확히 우수한 경우
- 단순한 워크플로우

#### 구조 (동적)

```
초기: Mesh (3 에이전트)
Agent1 ◄──► Agent2 ◄──► Agent3

에이전트 증가 (6개) → Star로 전환
        Hub
       / | \
      A1 A2 A3...A6

에이전트 증가 (12개) → Hierarchical로 전환
         Hub
        / | \
      M1  M2  M3
     /|  /|  /|
   E1 E2 E3 E4...
```

#### 성능 특성

- **메시지 지연**: 0.4ms (평균, 동적)
- **처리량**: 14,000 msg/s (10 에이전트)
- **확장성**: 우수 (자동 최적화)
- **장애 허용**: 중간 (현재 토폴로지에 따름)

#### 코드 예제

```python
from moai_flow.core.swarm_coordinator import SwarmCoordinator
from moai_flow.topology.adaptive import TopologyMode

# Adaptive 토폴로지 생성 (초기: Mesh)
coordinator = SwarmCoordinator(
    topology_type="adaptive",
    root_agent_id="alfred"
)

# 에이전트 등록 (자동 토폴로지 선택)
for i in range(1, 4):
    coordinator.register_agent(f"agent-{i}", {"type": "worker"})
# 현재: Mesh (3 에이전트)

# 에이전트 증가 → 자동으로 Star로 전환
for i in range(4, 8):
    coordinator.register_agent(f"agent-{i}", {"type": "worker"})
# 자동 전환: Mesh → Star (7 에이전트)

# 더 증가 → Hierarchical로 전환
for i in range(8, 15):
    coordinator.register_agent(f"agent-{i}", {"type": "worker"})
# 자동 전환: Star → Hierarchical (14 에이전트)

# 현재 토폴로지 확인
info = coordinator.get_topology_info()
print(f"Current topology: {info['topology_specific']['current_mode']}")
# Output: "hierarchical"
```

#### 자동 전환 규칙

**에이전트 수 기반**:
- 3-4개: Mesh (빠른 협업)
- 5-9개: Star (중앙 조정)
- 10+개: Hierarchical (확장성)

**작업 부하 기반**:
- 파이프라인 작업: Ring으로 전환
- 협업 작업: Mesh로 전환
- 관리 작업: Hierarchical로 전환

#### 사용 시나리오

**가변적인 프로젝트**:
- 초기 3명의 개발자로 시작 (Mesh)
- 프로젝트 성장으로 7명으로 증가 (Star)
- 대규모 출시 전 15명으로 확장 (Hierarchical)
- 유지보수 단계에서 5명으로 축소 (Star)

---

## 🔄 토폴로지 전환 전략

### 언제 전환해야 하나요?

#### Mesh → Star

**전환 시점**:
- 에이전트 수가 5개를 초과할 때
- 메시지 처리량이 감소할 때
- 네트워크 트래픽이 과도할 때

**전환 방법**:
```python
# 현재 Mesh 상태 확인
info = coordinator.get_topology_info()
if info["agent_count"] > 5:
    # Star로 전환
    coordinator.switch_topology("star")
```

#### Star → Hierarchical

**전환 시점**:
- 에이전트 수가 10개를 초과할 때
- 허브 병목이 발생할 때
- 역할 계층이 명확해질 때

**전환 방법**:
```python
if info["agent_count"] > 10:
    coordinator.switch_topology("hierarchical")
```

#### Mesh/Star → Ring

**전환 시점**:
- 작업이 파이프라인 형태로 변경될 때
- 순차 처리가 필요할 때
- 데이터 흐름이 단방향일 때

**전환 방법**:
```python
# 파이프라인 작업 감지
if is_pipeline_workflow(current_tasks):
    coordinator.switch_topology("ring")
```

---

## 📈 성능 벤치마크

### 메시지 처리 성능 (에이전트 수별)

```
Throughput (messages/second)
20K ┤
    │     Star ────────────
18K ┤           ╲
    │             ╲
16K ┤   Mesh       ╲   Hierarchical
    │      ╲         ╲     ────
14K ┤       ╲         ╲   ╱
    │        ╲         ╲ ╱
12K ┤         ╲         ╳
    │          ╲       ╱ ╲
10K ┤           ╲     ╱   ╲
    │            ╲   ╱     ╲
 8K ┤             ╲ ╱       ╲
    │              ╳         ╲
 6K ┤   Ring ────╱ ╲         ╲
    │          ╱     ╲         ╲
 4K ┼────────────────────────────
    3   5   7   9   11  13  15
           Agent Count
```

### 지연 시간 (에이전트 수별)

```
Latency (milliseconds)
2.0 ┤            Ring ───────
    │          ╱
1.5 ┤        ╱
    │      ╱
1.0 ┤    ╱
    │  ╱      Hierarchical ──
0.5 ┤╱  Mesh ╲    ───────
    │         ╲  ╱
0.0 ┤  Star ────╲───────────
    ┼────────────────────────
    3   5   7   9   11  13  15
           Agent Count
```

---

## 🎯 의사결정 플로우차트

```mermaid
graph TD
    A[에이전트 수는?] --> B{3-5개}
    A --> C{5-10개}
    A --> D{10개 이상}

    B --> E{작업 특성은?}
    E --> F[협업 중심] --> G[Mesh]
    E --> H[파이프라인] --> I[Ring]

    C --> J{중앙 조정 필요?}
    J --> K[예] --> L[Star]
    J --> M[아니오] --> N[Adaptive]

    D --> O{역할 계층 있음?}
    O --> P[예] --> Q[Hierarchical]
    O --> R[아니오] --> S[Adaptive]
```

---

## 💡 모범 사례

### 1. 초기 토폴로지 선택

**프로젝트 초기**:
- 3-5명 팀 → Mesh로 시작
- 명확한 역할 → Hierarchical로 시작
- 불확실한 경우 → Adaptive로 시작

### 2. 모니터링 및 최적화

**모니터링 지표**:
```python
# 주기적으로 토폴로지 상태 확인
info = coordinator.get_topology_info()

if info["health"] == "degraded":
    # 토폴로지 재평가
    if info["agent_count"] > 10 and info["type"] == "star":
        coordinator.switch_topology("hierarchical")
```

### 3. 장애 복구

**허브 실패 시나리오 (Star)**:
```python
# 허브 상태 확인
hub_status = coordinator.get_agent_status("alfred")

if hub_status["state"] == "failed":
    # Mesh로 긴급 전환
    coordinator.switch_topology("mesh")
```

### 4. 성능 최적화

**병목 감지 및 전환**:
```python
# 메시지 처리 지연 모니터링
if avg_latency > threshold:
    # 현재 Mesh이고 에이전트 증가 → Star로 전환
    if info["type"] == "mesh" and info["agent_count"] > 5:
        coordinator.switch_topology("star")
```

---

## 🔧 트러블슈팅

### 문제: Mesh에서 성능 저하

**증상**:
- 에이전트 수 증가 시 급격한 처리량 감소
- 네트워크 트래픽 폭증

**해결책**:
```python
# Star 또는 Hierarchical로 전환
if info["agent_count"] > 5:
    coordinator.switch_topology("star")
elif info["agent_count"] > 10:
    coordinator.switch_topology("hierarchical")
```

### 문제: Star에서 허브 병목

**증상**:
- 허브 메시지 큐 증가
- 전체 처리량 감소

**해결책**:
```python
# Hierarchical로 전환 (부하 분산)
coordinator.switch_topology("hierarchical")
```

### 문제: Ring에서 에이전트 실패

**증상**:
- 링 체인 끊김
- 메시지 전파 중단

**해결책**:
```python
# 실패 에이전트 제거 및 링 재구성
coordinator.unregister_agent("failed-agent")
# Ring 자동 재구성됨
```

---

## 📚 추가 자료

- [SwarmCoordinator Quickstart Guide](../moai_flow/docs/swarm_coordinator_quickstart.md)
- [SwarmCoordinator Implementation Guide](../moai_flow/docs/swarm_coordinator_implementation.md)
- [Phase 5 Completion Report](phases/PHASE-5-COMPLETION.md)
- [PRD-02: Swarm Coordination](../moai_flow/specs/PRD-02-swarm-coordination.md)

---

**작성자**: Alfred (workflow-docs agent)
**작성일**: 2025-11-29
**버전**: 1.0.0
**상태**: ✅ Phase 5 완료
