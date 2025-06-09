from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class EvaluationCriteriaView(APIView):
    def get(self, request):
        criteria = [
            {
                "name": "Mức độ tập trung",
                "code": "focus_score",
                "options": [
                    {"score": 1, "label": "Không tập trung: Thường xuyên mất tập trung, sao nhãng trong giờ học"},
                    {"score": 2, "label": "Ít tập trung: Thỉnh thoảng bị phân tán, cần nhắc nhở"},
                    {"score": 3, "label": "Tập trung khá: Duy trì được sự tập trung trong phần lớn thời gian"},
                    {"score": 4, "label": "Tập trung tốt: Rất chú ý, ít khi bị sao nhãng"},
                    {"score": 5, "label": "Hoàn toàn tập trung: Luôn giữ sự tập trung cao độ, chủ động tiếp thu"}
                ]
            },
            {
                "name": "Đi muộn/Trễ",
                "code": "punctuality_score",
                "options": [
                    {"score": 1, "label": "Thường xuyên đi muộn/về sớm: Rất ít khi đúng giờ"},
                    {"score": 2, "label": "Hay đi muộn/về sớm: Thường xuyên đến muộn hoặc về sớm"},
                    {"score": 3, "label": "Thỉnh thoảng đi muộn/về sớm: Có một vài lần không đúng giờ"},
                    {"score": 4, "label": "Hiếm khi đi muộn/về sớm: Gần như luôn đúng giờ"},
                    {"score": 5, "label": "Luôn đúng giờ: Chưa bao giờ đi muộn hay về sớm"}
                ]
            },
            {
                "name": "Mức độ tương tác",
                "code": "interaction_score",
                "options": [
                    {"score": 1, "label": "Thụ động: Không đặt câu hỏi, không tham gia thảo luận"},
                    {"score": 2, "label": "Ít tương tác: Hầu như không tham gia, chỉ trả lời khi được hỏi"},
                    {"score": 3, "label": "Tương tác trung bình: Tham gia khi có sự khuyến khích, đặt câu hỏi khi cần"},
                    {"score": 4, "label": "Tương tác tốt: Chủ động đặt câu hỏi, phát biểu ý kiến"},
                    {"score": 5, "label": "Tương tác xuất sắc: Luôn chủ động, tích cực tham gia xây dựng bài học"}
                ]
            },
            {
                "name": "Ý tưởng dự án",
                "code": "project_idea_score",
                "options": [
                    {"score": 1, "label": "Không có ý tưởng: Không thể đưa ra bất kỳ ý tưởng nào cho dự án"},
                    {"score": 2, "label": "Ý tưởng kém chất lượng: Ý tưởng chung chung, thiếu tính khả thi hoặc không liên quan"},
                    {"score": 3, "label": "Ý tưởng trung bình: Có ý tưởng nhưng chưa thực sự độc đáo hoặc cần phát triển thêm"},
                    {"score": 4, "label": "Ý tưởng tốt: Có ý tưởng rõ ràng, có tiềm năng phát triển"},
                    {"score": 5, "label": "Ý tưởng xuất sắc: Độc đáo, sáng tạo, có tính ứng dụng cao và đột phá"}
                ]
            },
            {
                "name": "Tư duy phản biện",
                "code": "critical_thinking_score",
                "options": [
                    {"score": 1, "label": "Không có tư duy phản biện: Chấp nhận mọi thông tin mà không phân tích"},
                    {"score": 2, "label": "Tư duy phản biện yếu: Khó khăn trong việc đặt câu hỏi, phân tích vấn đề"},
                    {"score": 3, "label": "Tư duy phản biện trung bình: Có thể đặt câu hỏi nhưng phân tích còn hời hợt"},
                    {"score": 4, "label": "Tư duy phản biện tốt: Có khả năng phân tích, đánh giá thông tin và đưa ra lập luận"},
                    {"score": 5, "label": "Tư duy phản biện xuất sắc: Luôn đặt câu hỏi, phân tích sâu sắc, nhìn nhận vấn đề đa chiều"}
                ]
            },
            {
                "name": "Hợp tác nhóm",
                "code": "teamwork_score",
                "options": [
                    {"score": 1, "label": "Không hợp tác: Từ chối hoặc gây cản trở trong làm việc nhóm"},
                    {"score": 2, "label": "Ít hợp tác: Tham gia miễn cưỡng, không đóng góp tích cực"},
                    {"score": 3, "label": "Hợp tác trung bình: Sẵn sàng làm việc nhóm nhưng chưa thực sự chủ động"},
                    {"score": 4, "label": "Hợp tác tốt: Tích cực tham gia, hỗ trợ các thành viên khác"},
                    {"score": 5, "label": "Hợp tác xuất sắc: Là nhân tố kết nối, thúc đẩy tinh thần làm việc nhóm"}
                ]
            },
            {
                "name": "Chia sẻ ý tưởng",
                "code": "idea_sharing_score",
                "options": [
                    {"score": 1, "label": "Không chia sẻ: Giữ ý tưởng cho riêng mình, không đóng góp"},
                    {"score": 2, "label": "Ít chia sẻ: Chỉ chia sẻ khi được yêu cầu, ngại bày tỏ"},
                    {"score": 3, "label": "Chia sẻ trung bình: Sẵn sàng chia sẻ nhưng chưa thực sự tự tin"},
                    {"score": 4, "label": "Chia sẻ tốt: Chủ động trình bày ý tưởng một cách rõ ràng"},
                    {"score": 5, "label": "Chia sẻ xuất sắc: Trình bày ý tưởng mạch lạc, thuyết phục, khuyến khích người khác"}
                ]
            },
            {
                "name": "Sáng tạo",
                "code": "creativity_score",
                "options": [
                    {"score": 1, "label": "Không sáng tạo: Chỉ làm theo những gì có sẵn, không có ý tưởng mới"},
                    {"score": 2, "label": "Ít sáng tạo: Khó khăn trong việc đưa ra giải pháp mới lạ"},
                    {"score": 3, "label": "Sáng tạo trung bình: Có khả năng tạo ra một số ý tưởng mới nhưng còn hạn chế"},
                    {"score": 4, "label": "Sáng tạo tốt: Thường xuyên đưa ra các ý tưởng và cách tiếp cận độc đáo"},
                    {"score": 5, "label": "Sáng tạo xuất sắc: Luôn có tư duy đột phá, tạo ra những giải pháp và sản phẩm độc đáo"}
                ]
            },
            {
                "name": "Giao tiếp",
                "code": "communication_score",
                "options": [
                    {"score": 1, "label": "Kém hiệu quả: Khó khăn trong việc diễn đạt ý kiến, gây hiểu lầm"},
                    {"score": 2, "label": "Chưa hiệu quả: Giao tiếp còn lúng túng, chưa rõ ràng"},
                    {"score": 3, "label": "Trung bình: Có thể truyền đạt thông tin nhưng đôi khi còn thiếu mạch lạc"},
                    {"score": 4, "label": "Tốt: Giao tiếp rõ ràng, mạch lạc, dễ hiểu"},
                    {"score": 5, "label": "Xuất sắc: Giao tiếp hiệu quả, thuyết phục, truyền cảm hứng"}
                ]
            },
            {
                "name": "Bài tập về nhà",
                "code": "homework_score",
                "options": [
                    {"score": 1, "label": "Không hoàn thành: Hầu như không làm hoặc nộp bài tập"},
                    {"score": 2, "label": "Hoàn thành kém chất lượng: Làm bài tập qua loa, thiếu nghiêm túc"},
                    {"score": 3, "label": "Hoàn thành trung bình: Làm bài tập đầy đủ nhưng chất lượng chưa cao"},
                    {"score": 4, "label": "Hoàn thành tốt: Làm bài tập đầy đủ, chất lượng tốt, đúng hạn"},
                    {"score": 5, "label": "Hoàn thành xuất sắc: Luôn làm bài tập đầy đủ, chất lượng vượt trội, có sự tìm tòi"}
                ]
            },
            {
                "name": "Kiến thức cũ",
                "code": "prior_knowledge_score",
                "options": [
                    {"score": 1, "label": "Không nắm vững: Quên hoặc không hiểu các kiến thức đã học trước đó"},
                    {"score": 2, "label": "Nắm vững yếu: Nắm được một phần nhưng còn mơ hồ"},
                    {"score": 3, "label": "Nắm vững trung bình: Nhớ và hiểu các kiến thức cơ bản"},
                    {"score": 4, "label": "Nắm vững tốt: Hiểu sâu sắc và có thể ứng dụng kiến thức cũ"},
                    {"score": 5, "label": "Nắm vững xuất sắc: Thành thạo kiến thức cũ, có thể liên hệ và mở rộng"}
                ]
            },
            {
                "name": "Kiến thức mới",
                "code": "new_knowledge_score",
                "options": [
                    {"score": 1, "label": "Khó tiếp thu: Gặp rất nhiều khó khăn trong việc hiểu kiến thức mới"},
                    {"score": 2, "label": "Tiếp thu chậm: Cần nhiều thời gian và sự hỗ trợ để hiểu"},
                    {"score": 3, "label": "Tiếp thu trung bình: Tiếp thu được kiến thức mới nhưng cần ôn tập thêm"},
                    {"score": 4, "label": "Tiếp thu tốt: Nắm bắt kiến thức mới nhanh chóng và hiệu quả"},
                    {"score": 5, "label": "Tiếp thu xuất sắc: Tiếp thu rất nhanh, có khả năng phân tích và tổng hợp kiến thức mới"}
                ]
            }
        ]
        return Response(criteria, status=status.HTTP_200_OK) 