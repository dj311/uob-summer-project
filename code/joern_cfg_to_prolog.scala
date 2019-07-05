import gremlin.scala._
import io.shiftleft.codepropertygraph.generated._
import java.nio.file.Paths
import io.shiftleft.queryprimitives.utils.ExpandTo
import org.apache.tinkerpop.gremlin.structure.Direction
import io.shiftleft.queryprimitives.steps.Implicits.JavaIteratorDeco
import javax.script.ScriptEngineManager
import scala.io.Source

/* APACHE from https://github.com/shiftleftsecurity/joern/ */
/* TODO: license properly */


/** Some helper functions: adapted from ReachingDefPass.scala in codeproperty graph repo */
def vertexToStr(vertex: Vertex, identifiers: Map[Vertex,Int]): String = {
  try {
    val methodVertex = vertex.vertices(Direction.IN, "CONTAINS").nextChecked
    val fileName = methodVertex.vertices(Direction.IN, "CONTAINS").nextChecked match {
      case file: nodes.File => file.asInstanceOf[nodes.File].name
      case _ => "NA"
    }
    val filename_temp = Paths.get(fileName).getFileName.toString
    val newfile_name = filename_temp.replaceAll("CWE.*__CWE[0-9]+_", "").replaceAll("\\.", "_")
    s"${identifiers(vertex).toString}_${newfile_name}_${vertex.value2(NodeKeys.LINE_NUMBER).toString}_${vertex.value2(NodeKeys.COLUMN_NUMBER).toString}"
  } catch { case _: Exception => identifiers(vertex).toString }
}

def toProlog(graph: ScalaGraph): String = {
  var vertex_identifiers:Map[Vertex,Int] = Map()

  var index = 0
  graph.V.l.foreach{ v =>
    vertex_identifiers += (v -> index)
    index += 1
  }

  val buf = new StringBuffer()

  buf.append("% START: Generated Prolog\n")

  buf.append("% AST\n")
  graph.E.hasLabel("AST").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""ast($parentVertex, $childVertex).\n """)
  }

  buf.append("% CFG\n")
  graph.E.hasLabel("CFG").l.foreach { e =>
    val parentVertex = vertexToStr(e.outVertex, vertex_identifiers).replace("\"","\'")
    val childVertex = vertexToStr(e.inVertex, vertex_identifiers).replace("\"","\'")
    buf.append(s"""cfg($parentVertex, $childVertex).\n """)
  }

  buf.append("% END: Generated Prolog ")

  buf.toString
}

toProlog(cpg.graph)
