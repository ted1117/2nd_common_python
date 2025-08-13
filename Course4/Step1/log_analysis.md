
# 사고 원인 분석 보고서

## 1. 개요

본 보고서는 `mission_computer_main.log` 파일을 기반으로 로켓 임무 수행 중 발생한 사고의 원인을 분석하기 위한 보고서이다.

## 2. 사고 발생 타임라인
- **2023-08-27 11:28:00**: Touchdown confirmed. Rocket safely landed.
- **2023-08-27 11:35:00**: Oxygen tank unstable.
- **2023-08-27 11:40:00**: Oxygen tank explosion.

## 3. 사고 원인 분석

1.  **임무 완료 후 문제 발생**: 로그에 따르면 로켓은 **11:28:00**에 안전하게 착륙(`Touchdown confirmed. Rocket safely landed.`)했고, **11:30:00**에 임무 성공(`Mission completed successfully.`)이 선언되었다.
2.  **산소 탱크 이상 징후**: 착륙 7분 후인 **11:35:00**에 `Oxygen tank unstable` 로그가 기록되며 산소 탱크가 불안정한 상태임이 처음으로 감지되었다.
3.  **폭발 발생**: 이상 징후 감지 5분 후인 **11:40:00**에 `Oxygen tank explosion` 로그가 기록되며 실제 폭발이 발생했다.

## 4. 결론

사고의 직접적인 원인은 **산소 탱크의 폭발**이다.

로켓이 지상에 안전하게 착륙했으나, 산소 탱크에 원인 불명의 문제로 인해 불안정한 상태가 발발되었고, 폭발로 이어졌다.

